use std::path::PathBuf;

use bevy::{gltf::Gltf, prelude::*, scene::SceneInstance, utils::hashbrown::HashMap};
use serde_json::Value;

use crate::{
    AnimationInfos, AssetLoadTracker, AssetToBlueprintInstancesMapper, BlenvyConfig, BlueprintAnimationInfosLink, BlueprintAnimationPlayerLink, BlueprintAnimations, BlueprintAssets, BlueprintAssetsLoadState, BlueprintAssetsLoaded, BlueprintAssetsNotLoaded, SceneAnimationInfosLink, SceneAnimationPlayerLink, SceneAnimations
};

/// this is a flag component for our levels/game world
#[derive(Component)]
pub struct GameWorldTag;

/// Main component for the blueprints
/// has both name & path of the blueprint to enable injecting the data from the correct blueprint
/// into the entity that contains this component
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct BlueprintInfo {
    pub name: String,
    pub path: String,
}
use std::path::Path;

impl BlueprintInfo {
    pub fn from_path(path: &str) -> BlueprintInfo {
        let p = Path::new(&path);
        return BlueprintInfo {
            name: p.file_stem().unwrap().to_os_string().into_string().unwrap(), // seriously ? , also unwraps !!
            path: path.into(),
        };
    }
}

/// flag component needed to signify the intent to spawn a Blueprint
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct SpawnBlueprint;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component marking any spwaned child of blueprints 
pub struct FromBlueprint;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component to force adding newly spawned entity as child of game world
pub struct AddToGameWorld;

#[derive(Component)]
/// helper component, just to transfer child data
pub(crate) struct OriginalChildren(pub Vec<Entity>);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// You can add this component to a blueprint instance, and the instance will be hidden until it is ready
/// You usually want to use this for worlds/level spawning , or dynamic spawning at runtime, but not when you are adding blueprint instances to an existing entity
/// as it would first become invisible before re-appearing again
pub struct HideUntilReady;

#[derive(Component)]
/// marker component, gets added to all children of a currently spawning blueprint instance, can be usefull to avoid manipulating still in progress entities
pub struct BlueprintInstanceDisabled;

#[derive(Event, Debug)]
pub enum BlueprintEvent {
    /// event fired when a blueprint instance has finished loading all of its assets & before it attempts spawning
    AssetsLoaded {
        entity: Entity,
        blueprint_name: String,
        blueprint_path: String,
        // TODO: add assets list ?
    },

    /// event fired when a blueprint instance has completely finished spawning, ie
    /// - all its assests have been loaded
    /// - all of its child blueprint instances are ready
    /// - all the post processing is finished (aabb calculation, material replacements etc)
    InstanceReady {
        entity: Entity,
        blueprint_name: String,
        blueprint_path: String,
    },
}

// TODO: move this somewhere else ?
#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
/// component used to mark any entity as Dynamic: aka add this to make sure your entity is going to be saved
pub struct DynamicBlueprintInstance;

// TODO: move these somewhere else ?
#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
/// component gets added when a blueprint starts spawning, removed when spawning is completely done
pub struct BlueprintSpawning;

use gltf::Gltf as RawGltf;




/*
Overview of the Blueprint Spawning process
    - Blueprint Load Assets
    - Blueprint Assets Ready: spawn Blueprint's scene
    - Blueprint Scene Ready (SceneInstance component is present):
        - get list of sub Blueprints if any, inject sub blueprints spawn tracker
    - Blueprint copy components to original entity, remove useless nodes
    - Blueprint post process
        - generate aabb (need full hierarchy in its final form)
        - inject materials from library if needed
    - Blueprint Ready
        - bubble information up to parent blueprint instance
        - if all sub_blueprints are ready => Parent blueprint Instance is ready
 => distinguish between blueprint instances inside blueprint instances vs blueprint instances inside blueprints ??
*/

pub(crate) fn blueprints_prepare_spawn(
    blueprint_instances_to_spawn: Query<
        (Entity, &BlueprintInfo, Option<&Name>),
        Added<SpawnBlueprint>,
    >,
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    // for hot reload
    mut assets_to_blueprint_instances: ResMut<AssetToBlueprintInstancesMapper>,
    // for debug
    all_names: Query<&Name>
) {
    for (entity, blueprint_info, entity_name) in blueprint_instances_to_spawn.iter() {
        info!(
            "BLUEPRINT: to spawn detected: {:?} path:{:?}",
            blueprint_info.name, blueprint_info.path
        );
        //println!("all assets {:?}", all_assets);
        //////////////
        // we add the asset of the blueprint itself
        // TODO: add detection of already loaded data
        let untyped_handle = asset_server.load_untyped(&blueprint_info.path);
        let asset_id = untyped_handle.id();
        let loaded = asset_server.is_loaded_with_dependencies(asset_id);

        let mut asset_infos: Vec<AssetLoadTracker> = vec![];
        if !loaded {
            asset_infos.push(AssetLoadTracker {
                name: blueprint_info.name.clone(),
                path: blueprint_info.path.clone(),
                id: asset_id,
                loaded: false,
                handle: untyped_handle.clone(),
            });
        }

        // and we also add all its assets
        /* prefetch attempt */
        let gltf = RawGltf::open(format!("assets/{}", blueprint_info.path)).unwrap();
        for scene in gltf.scenes() {
            let scene_extras = scene.extras().clone().unwrap();
            let lookup: HashMap<String, Value> = serde_json::from_str(scene_extras.get()).unwrap();
            if lookup.contains_key("BlueprintAssets") {
                let assets_raw = &lookup["BlueprintAssets"];
                //println!("ASSETS RAW {}", assets_raw);
                let all_assets: BlueprintAssets =
                    ron::from_str(assets_raw.as_str().unwrap()).unwrap();
                // println!("all_assets {:?}", all_assets);

                for asset in all_assets.assets.iter() {
                    println!("ASSET {}",asset.path);
                    let untyped_handle = asset_server.load_untyped(&asset.path);
                    let asset_id = untyped_handle.id();
                    let loaded = asset_server.is_loaded_with_dependencies(asset_id);
                    if !loaded {
                        asset_infos.push(AssetLoadTracker {
                            name: asset.name.clone(),
                            path: asset.path.clone(),
                            id: asset_id,
                            loaded: false,
                            handle: untyped_handle.clone(),
                        });
                    }

                    // FIXME: dang, too early, asset server has not yet started loading yet
                    // let path_id = asset_server.get_path_id(&asset.path).expect("we should have alread checked for this asset");
                    let path_id = asset.path.clone();
                    // TODO: make this dependant on if hot reload is enabled or not
                    if !assets_to_blueprint_instances.untyped_id_to_blueprint_entity_ids.contains_key(&path_id) {
                        assets_to_blueprint_instances.untyped_id_to_blueprint_entity_ids.insert(path_id.clone(), vec![]);
                    }
                    // only insert if not already present in mapping
                    if !assets_to_blueprint_instances.untyped_id_to_blueprint_entity_ids[&path_id].contains(&entity) {
                        println!("adding mapping between {} and entity {:?}", path_id, all_names.get(entity));
                        assets_to_blueprint_instances.untyped_id_to_blueprint_entity_ids.get_mut(&path_id).unwrap().push(entity);
                    }
                }
            }
        }

        // now insert load tracker
        // if there are assets to load
        if !asset_infos.is_empty() {
            commands.entity(entity).insert((
                BlueprintAssetsLoadState {
                    all_loaded: false,
                    asset_infos,
                    ..Default::default()
                },
                BlueprintAssetsNotLoaded,
            ));
        } else {
            commands.entity(entity).insert(BlueprintAssetsLoaded);
        }

        // if the entity has no name, add one based on the blueprint's
        commands
            .entity(entity)
            .insert(bevy::prelude::Name::from(blueprint_info.name.clone()));
        // add the blueprint spawning marker
        commands.entity(entity).insert(BlueprintSpawning);
    }
}

/// This system tracks & updates the loading state of all blueprints assets
pub(crate) fn blueprints_check_assets_loading(
    mut blueprint_assets_to_load: Query<
        (Entity, &BlueprintInfo, &mut BlueprintAssetsLoadState),
        With<BlueprintAssetsNotLoaded>,
    >,
    asset_server: Res<AssetServer>,
    mut commands: Commands,
    mut blueprint_events: EventWriter<BlueprintEvent>,
) {
    for (entity, blueprint_info, mut assets_to_load) in blueprint_assets_to_load.iter_mut() {
        let mut all_loaded = true;
        let mut loaded_amount = 0;
        let total = assets_to_load.asset_infos.len();
        for tracker in assets_to_load.asset_infos.iter_mut() {
            let asset_id = tracker.id;
            let loaded = asset_server.is_loaded_with_dependencies(asset_id);

            let mut failed = false;
            if let bevy::asset::LoadState::Failed(_) = asset_server.load_state(asset_id) { failed = true }
            tracker.loaded = loaded || failed;
            if loaded || failed {
                loaded_amount += 1;
            } else {
                all_loaded = false;
            }
        }
        let progress: f32 = loaded_amount as f32 / total as f32;
        assets_to_load.progress = progress;
        // println!("LOADING: in progress for ALL assets of {:?} (instance of {}): {} ",entity_name, blueprint_info.path, progress * 100.0);

        if all_loaded {
            assets_to_load.all_loaded = true;
            // println!("LOADING: DONE for ALL assets of {:?} (instance of {}), preparing for spawn", entity_name, blueprint_info.path);
            blueprint_events.send(BlueprintEvent::AssetsLoaded {
                entity,
                blueprint_name: blueprint_info.name.clone(),
                blueprint_path: blueprint_info.path.clone(),
            });

            commands
                .entity(entity)
                .insert(BlueprintAssetsLoaded)
                .remove::<BlueprintAssetsNotLoaded>()
                //.remove::<BlueprintAssetsLoadState>() //REMOVE this component in release mode/ when hot reload is off, keep it for dev/hot reload
                ;
        }
    }
}

pub(crate) fn blueprints_assets_loaded(
    spawn_placeholders: Query<
        (
            Entity,
            &BlueprintInfo,
            Option<&Transform>,
            Option<&Parent>,
            Option<&AddToGameWorld>,
            Option<&Name>,
            Option<&HideUntilReady>,
            Option<&AnimationInfos>,
        ),
        (
            With<BlueprintAssetsLoaded>,
            Added<BlueprintAssetsLoaded>,
            Without<BlueprintAssetsNotLoaded>,
        ),
    >,
    all_children: Query<&Children>,
    mut game_world: Query<Entity, With<GameWorldTag>>,
    assets_gltf: Res<Assets<Gltf>>,
    asset_server: Res<AssetServer>,

    mut graphs: ResMut<Assets<AnimationGraph>>,

    mut commands: Commands,
) {
    for (
        entity,
        blueprint_info,
        transform,
        original_parent,
        add_to_world,
        name,
        hide_until_ready,
        animation_infos,
    ) in spawn_placeholders.iter()
    {
        /*info!(
            "BLUEPRINT: all assets loaded, attempting to spawn blueprint SCENE {:?} for entity {:?}, id: {:}, parent:{:?}",
            blueprint_info.name, name, entity, original_parent
        );*/

        info!(
            "BLUEPRINT: all assets loaded, attempting to spawn blueprint SCENE {:?} for entity {:?}, id: {}",
            blueprint_info.name, name, entity
        );

        // info!("attempting to spawn {:?}", model_path);
        let model_handle: Handle<Gltf> = asset_server.load(blueprint_info.path.clone()); // FIXME: kinda weird now

        let blueprint_gltf = assets_gltf.get(&model_handle).unwrap_or_else(|| {
            panic!(
                "gltf file {:?} should have been loaded",
                &blueprint_info.path
            )
        });

        // WARNING we work under the assumtion that there is ONLY ONE named scene, and that the first one is the right one
        let main_scene_name = blueprint_gltf
            .named_scenes
            .keys()
            .next()
            .expect("there should be at least one named scene in the gltf file to spawn");

        let scene = &blueprint_gltf.named_scenes[main_scene_name];

        // transforms are optional, but still deal with them correctly
        let mut transforms: Transform = Transform::default();
        if transform.is_some() {
            transforms = *transform.unwrap();
        }

        let mut original_children: Vec<Entity> = vec![];
        if let Ok(c) = all_children.get(entity) {
            for child in c.iter() {
                original_children.push(*child);
            }
        }

        // TODO: not a fan of this
        // prepare data for animations
        let mut graph = AnimationGraph::new();
        let mut named_animations: HashMap<String, Handle<AnimationClip>> = HashMap::new();
        let mut animation_indices: HashMap<String, AnimationNodeIndex> = HashMap::new();

        for (key, clip) in blueprint_gltf.named_animations.iter() {
            named_animations.insert(key.to_string(), clip.clone());
            let animation_index = graph.add_clip(clip.clone(), 1.0, graph.root);
            animation_indices.insert(key.to_string(), animation_index);
        }
        let graph = graphs.add(graph);

        println!("Named animations : {:?}", named_animations.keys());
        println!("ANIMATION INFOS: {:?}", animation_infos);

        commands.entity(entity).insert((
            SceneBundle {
                scene: scene.clone(),
                transform: transforms,
                ..Default::default()
            },
            OriginalChildren(original_children),
            BlueprintAnimations {
                // TODO: perhaps swap this out with SceneAnimations depending on whether we are spawning a level or a simple blueprint
                // these are animations specific to the blueprint
                named_animations,
                named_indices: animation_indices,
                graph,
            },
        ));

        if original_parent.is_none() {
            // only allow hiding until ready when the entity does not have a parent (?)
            if hide_until_ready.is_some() {
                commands.entity(entity).insert(Visibility::Hidden); // visibility:
            }

            // only allow automatically adding a newly spawned blueprint instance to the "world", if the entity does not have a parent
            if add_to_world.is_some() {
                let world = game_world
                    .get_single_mut()
                    .expect("there should be a game world present");
                commands.entity(world).add_child(entity);
            }
        }
    }
}

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct SubBlueprintsSpawnTracker {
    pub sub_blueprint_instances: HashMap<Entity, bool>,
}

#[derive(Component, Reflect, Debug)]
#[reflect(Component)]
pub struct SubBlueprintSpawnRoot(pub Entity);

#[derive(Component, Reflect, Debug)]
#[reflect(Component)]
pub struct BlueprintSceneSpawned;

#[derive(Component, Reflect, Debug)]
#[reflect(Component)]
pub struct BlueprintChildrenReady;

pub(crate) fn blueprints_scenes_spawned(
    spawned_blueprint_scene_instances: Query<
        (
            Entity,
            Option<&Name>,
            Option<&Children>,
            Option<&SubBlueprintSpawnRoot>,
        ),
        (With<BlueprintSpawning>, Added<SceneInstance>),
    >,
    with_blueprint_infos: Query<(Entity, Option<&Name>), With<BlueprintInfo>>,

    all_children: Query<&Children>,
    all_parents: Query<&Parent>,

    // mut sub_blueprint_trackers: Query<(Entity, &mut SubBlueprintsSpawnTracker, &BlueprintInfo)>,
    mut commands: Commands,

    all_names: Query<&Name>,
) {
    for (entity, name, children, track_root) in spawned_blueprint_scene_instances.iter() {
        info!(
            "Done spawning blueprint scene for entity named {:?} (track root: {:?})",
            name, track_root
        );
        let mut sub_blueprint_instances: Vec<Entity> = vec![];
        let mut sub_blueprint_instance_names: Vec<Name> = vec![];
        let mut tracker_data: HashMap<Entity, bool> = HashMap::new();

        if track_root.is_none() {
            for parent in all_parents.iter_ancestors(entity) {
                if with_blueprint_infos.get(parent).is_ok() {
                    println!(
                        "found a parent with blueprint_info {:?} for {:?}",
                        all_names.get(parent),
                        all_names.get(entity)
                    );
                    commands
                        .entity(entity)
                        .insert(SubBlueprintSpawnRoot(parent)); // Injecting to know which entity is the root
                    break;
                }
            }
        }

        if children.is_some() {
            for child in all_children.iter_descendants(entity) {
                if with_blueprint_infos.get(child).is_ok() {
                    // println!("Parent blueprint instance of {:?} is {:?}",  all_names.get(child), all_names.get(entity));
                    for parent in all_parents.iter_ancestors(child) {
                        if with_blueprint_infos.get(parent).is_ok() {
                            if parent == entity {
                                //println!("yohoho");
                                println!(
                                    "Parent blueprint instance of {:?} is {:?}",
                                    all_names.get(child),
                                    all_names.get(parent)
                                );

                                commands.entity(child).insert(SubBlueprintSpawnRoot(entity)); // Injecting to know which entity is the root

                                tracker_data.insert(child, false);

                                sub_blueprint_instances.push(child);
                                if let Ok(nname) = all_names.get(child) {
                                    sub_blueprint_instance_names.push(nname.clone());
                                }
                                /*if track_root.is_some() {
                                    let prev_root = track_root.unwrap().0;
                                    // if we already had a track root, and it is different from the current entity , change the previous track root's list of children
                                    if prev_root != entity {
                                        let mut tracker = sub_blueprint_trackers.get_mut(prev_root).expect("should have a tracker");
                                        tracker.1.sub_blueprint_instances.remove(&child);
                                    }
                                }*/
                            }
                            break;
                        }
                    }
                }
                // Mark all components as "Disabled" (until Bevy gets this as first class feature)
                commands.entity(child).insert(BlueprintInstanceDisabled);
            }
        }

        println!("sub blueprint instances {:?}", sub_blueprint_instance_names);

        if tracker_data.keys().len() > 0 {
            commands.entity(entity).insert(SubBlueprintsSpawnTracker {
                sub_blueprint_instances: tracker_data.clone(),
            });
        } else {
            commands.entity(entity).insert(BlueprintChildrenReady);
        }
    }
}

// could be done differently, by notifying each parent of a spawning blueprint that this child is done spawning ?
// perhaps using component hooks or observers (ie , if a ComponentSpawning + Parent)
use crate::CopyComponents;
use std::any::TypeId;

#[derive(Component, Reflect, Debug)]
#[reflect(Component)]
pub struct BlueprintReadyForPostProcess;

/// this system is in charge of doing component transfers & co
/// - it removes one level of useless nesting
/// - it copies the blueprint's root components to the entity it was spawned on (original entity)
/// - it copies the children of the blueprint scene into the original entity
/// - it adds an `AnimationLink` component containing the entity that has the `AnimationPlayer` so that animations can be controlled from the original entity
pub(crate) fn blueprints_cleanup_spawned_scene(
    blueprint_scenes: Query<
        (
            Entity,
            &Children,
            &OriginalChildren,
            Option<&Name>,
            &BlueprintAnimations,
        ),
        Added<BlueprintChildrenReady>,
    >,
    animation_players: Query<(Entity, &Parent), With<AnimationPlayer>>,
    all_children: Query<&Children>,
    all_parents: Query<&Parent>,
    with_animation_infos: Query<&AnimationInfos>,
    // FIXME: meh
    anims: Query<&BlueprintAnimations>,

    mut commands: Commands,

    all_names: Query<&Name>,
) {
    for (original, children, original_children, name, animations) in
        blueprint_scenes.iter()
    {
        info!("YOOO ready !! removing empty nodes {:?}", name);

        if children.len() == 0 {
            warn!("timing issue ! no children found, please restart your bevy app (bug being investigated)");
            continue;
        }
        // the root node is the first & normally only child inside a scene, it is the one that has all relevant components
        let mut blueprint_root_entity = Entity::PLACEHOLDER; //FIXME: and what about childless ones ?? => should not be possible normally
                                                             // let diff = HashSet::from_iter(original_children.0).difference(HashSet::from_iter(children));
                                                             // we find the first child that was not in the entity before (aka added during the scene spawning)
        for child in children.iter() {
            if !original_children.0.contains(child) {
                blueprint_root_entity = *child;
                break;
            }
        }

        // we flag all children of the blueprint instance with 'FromBlueprint'
        // can be usefull to filter out anything that came from blueprints vs normal children
        for child in all_children.iter_descendants(blueprint_root_entity) {
            commands.entity(child).insert(FromBlueprint); // we do this here in order to avoid doing it to normal children
        }
        

        // copy components into from blueprint instance's blueprint_root_entity to original entity
        commands.add(CopyComponents {
            source: blueprint_root_entity,
            destination: original,
            exclude: vec![TypeId::of::<Parent>(), TypeId::of::<Children>()],
            stringent: false,
        });

        // we move all of children of the blueprint instance one level to the original entity to avoid having an additional, useless nesting level
        if let Ok(root_entity_children) = all_children.get(blueprint_root_entity) {
            for child in root_entity_children.iter() {
                // info!("copying child {:?} upward from {:?} to {:?}", names.get(*child), blueprint_root_entity, original);
                commands.entity(original).add_child(*child);
            }
        }

        if animations.named_animations.keys().len() > 0 {
            for (entity_with_player, parent) in animation_players.iter() {
                if parent.get() == blueprint_root_entity {
                    println!(
                        "FOUND ANIMATION PLAYER FOR {:?} {:?} ",
                        all_names.get(original),
                        all_names.get(entity_with_player)
                    );
                    // FIXME: stopgap solution: since we cannot use an AnimationPlayer at the root entity level
                    // and we cannot update animation clips so that the EntityPaths point to one level deeper,
                    // BUT we still want to have some marker/control at the root entity level, we add this
                    commands
                        .entity(original)
                        .insert((BlueprintAnimationPlayerLink(entity_with_player),)); // FIXME : this is only valid for per-blueprint logic, no per scene animations

                    // since v0.14 you need both AnimationTransitions and AnimationGraph components/handle on the same entity as the animationPlayer
                    let transitions = AnimationTransitions::new();
                    commands
                        .entity(entity_with_player)
                        .insert((transitions, animations.graph.clone()));
                }
            }
            // VERY convoluted, but it works
            for child in all_children.iter_descendants(blueprint_root_entity) {
                if with_animation_infos.get(child).is_ok() {
                    // player is already on the same entity as the animation_infos
                    if animation_players.get(child).is_ok() {
                        println!(
                            "found BLUEPRINT animation player for {:?} at {:?} Root: {:?}",
                            all_names.get(child),
                            all_names.get(child),
                            all_names.get(original)
                        );
                        commands
                        .entity(original)
                        .insert((
                            //BlueprintAnimationPlayerLink(bla),
                            BlueprintAnimationInfosLink(child)
                        ))
                        ;

                    } else {
                        for parent in all_parents.iter_ancestors(child) {
                            if animation_players.get(parent).is_ok() {
                                println!(
                                    "found SCENE animation player for {:?} at {:?} Root: {:?}",
                                    all_names.get(child),
                                    all_names.get(parent),
                                    all_names.get(original)
                                );
                                println!("INSERTING SCENE ANIMATIONS INTO");
                                let original_animations = anims.get(original).unwrap();
                                commands.entity(child).insert((
                                    SceneAnimationPlayerLink(parent),
                                    SceneAnimations {
                                        named_animations: original_animations
                                            .named_animations
                                            .clone(),
                                        named_indices: original_animations.named_indices.clone(),
                                        graph: original_animations.graph.clone(),
                                    },
                                ));
                            }
                            if with_animation_infos.get(parent).is_ok() {
                                commands.entity(child).insert(SceneAnimationInfosLink(parent));

                            }
                        }
                    }
                }
            }
        }

        commands
            .entity(original)
            .remove::<BlueprintChildrenReady>() // we are done with this step, we can remove the `BlueprintChildrenReady` tag component
            .insert(BlueprintReadyForPostProcess); // Tag the entity so any systems dealing with post processing can know it is now their "turn"

        commands.entity(blueprint_root_entity).despawn_recursive(); // Remove the root entity that comes from the spawned-in scene
    }
}

#[derive(Component, Reflect, Debug)]
#[reflect(Component)]
pub struct BlueprintReadyForFinalizing;

#[derive(Component, Debug)]
/// flag component added when a Blueprint instance ist Ready : ie :
/// - its assets have loaded
/// - it has finished spawning
pub struct BlueprintInstanceReady;

pub(crate) fn blueprints_finalize_instances(
    blueprint_instances: Query<
        (
            Entity,
            Option<&Name>,
            &BlueprintInfo,
            Option<&SubBlueprintSpawnRoot>,
            Option<&HideUntilReady>,
        ),
        (With<BlueprintSpawning>, With<BlueprintReadyForFinalizing>),
    >,
    mut sub_blueprint_trackers: Query<&mut SubBlueprintsSpawnTracker, With<BlueprintInfo>>,
    spawning_blueprints: Query<&BlueprintSpawning>,
    all_children: Query<&Children>,
    mut blueprint_events: EventWriter<BlueprintEvent>,
    mut commands: Commands,

    all_names: Query<&Name>
) {
    for (entity, name, blueprint_info, parent_blueprint, hide_until_ready) in
        blueprint_instances.iter()
    {
        info!("Finalizing blueprint instance {:?}", name);
        commands
            .entity(entity)
            .remove::<BlueprintReadyForFinalizing>()
            .remove::<BlueprintReadyForPostProcess>()
            .remove::<BlueprintSpawning>()
            .remove::<SpawnBlueprint>()
            //.remove::<Handle<Scene>>(); // FIXME: if we delete the handle to the scene, things get despawned ! not what we want
            //.remove::<BlueprintAssetsLoadState>(); // also clear the sub assets tracker to free up handles, perhaps just freeing up the handles and leave the rest would be better ?
            //.remove::<BlueprintAssetsLoaded>();
            .insert(BlueprintInstanceReady);

        // Deal with sub blueprints
        // now check if the current entity is a child blueprint instance of another entity
        // this should always be done last, as children should be finished before the parent can be processed correctly
        // TODO: perhaps use observers for these
        if let Some(track_root) = parent_blueprint {
            // only propagate sub_blueprint spawning if the parent blueprint instance ist actually in spawning mode
            if spawning_blueprints.get(track_root.0).is_ok() {
                if let Ok(mut tracker) = sub_blueprint_trackers.get_mut(track_root.0) {
                    tracker
                        .sub_blueprint_instances
                        .entry(entity)
                        .or_insert(true);
                    tracker.sub_blueprint_instances.insert(entity, true);

                    // TODO: ugh, my limited rust knowledge, this is bad code
                    let mut all_spawned = true;
                    for val in tracker.sub_blueprint_instances.values() {
                        if !val {
                            all_spawned = false;
                            break;
                        }
                    }
                    if all_spawned {
                        
                            let root_name = all_names.get(track_root.0);
                            println!("ALLLLL SPAAAAWNED for {} named {:?}", track_root.0, root_name);
                            commands.entity(track_root.0).insert(BlueprintChildrenReady);

                    }
                }
            }
        }

        for child in all_children.iter_descendants(entity) {
            commands.entity(child).remove::<BlueprintInstanceDisabled>();
        }

        if hide_until_ready.is_some() {
            commands.entity(entity).insert(Visibility::Visible);
        }

        blueprint_events.send(BlueprintEvent::InstanceReady {
            entity,
            blueprint_name: blueprint_info.name.clone(),
            blueprint_path: blueprint_info.path.clone(),
        });
    }
}
