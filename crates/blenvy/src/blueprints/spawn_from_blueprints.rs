use std::path::{Path, PathBuf};

use bevy::{asset::LoadedUntypedAsset, gltf::Gltf, prelude::*, render::view::visibility, scene::SceneInstance, transform::commands, utils::{hashbrown::HashMap}};
use serde_json::Value;

use crate::{BlueprintAssets, BlueprintAssetsLoadState, AssetLoadTracker, BlenvyConfig, BlueprintAnimations, BlueprintAssetsLoaded, BlueprintAssetsNotLoaded};

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

/// flag component needed to signify the intent to spawn a Blueprint
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct SpawnHere;

#[derive(Component)]
/// flag component for dynamically spawned scenes
pub struct Spawned;


#[derive(Component, Debug)]
/// flag component added when a Blueprint instance ist Ready : ie : 
/// - its assets have loaded
/// - it has finished spawning
pub struct BlueprintInstanceReady;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component marking any spwaned child of blueprints ..unless the original entity was marked with the `NoInBlueprint` marker component
pub struct InBlueprint;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component preventing any spawned child of blueprints to be marked with the `InBlueprint` component
pub struct NoInBlueprint;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
// this allows overriding the default library path for a given entity/blueprint
pub struct Library(pub PathBuf);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component to force adding newly spawned entity as child of game world
pub struct AddToGameWorld;

#[derive(Component)]
/// helper component, just to transfer child data
pub(crate) struct OriginalChildren(pub Vec<Entity>);


#[derive(Event, Debug)]
pub enum BlueprintEvent {

    /// event fired when a blueprint has finished loading its assets & before it attempts spawning
    AssetsLoaded {
        entity: Entity,
        blueprint_name: String,
        blueprint_path: String,
        // TODO: add assets list ?
    },
    /// event fired when a blueprint is COMPLETELY done spawning ie
    /// - all its assets have been loaded
    /// - the spawning attempt has been sucessfull
    Spawned {
        entity: Entity,
        blueprint_name: String,
        blueprint_path: String,
    },

    /// 
    Ready {
        entity: Entity,
        blueprint_path: String,
    }
    
}


// TODO: move this somewhere else ?
#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
/// component used to mark any entity as Dynamic: aka add this to make sure your entity is going to be saved
pub struct DynamicBlueprintInstance;


// TODO: move these somewhere else ?
#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
/// component gets added when a blueprint starts spawning, removed when spawning is done
pub struct BlueprintSpawning;


#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
/// component gets added when a blueprint spawning is done
pub struct BlueprintSpawned;


use gltf::Gltf as RawGltf;

pub(crate) fn blueprints_prepare_spawn(
    blueprint_instances_to_spawn : Query<
    (
        Entity,
        &BlueprintInfo,
        Option<&Parent>,
        Option<&BlueprintAssets>,
    ),(Added<SpawnHere>)
    >,
mut commands: Commands,
asset_server: Res<AssetServer>,
) {
   
    for (entity, blueprint_info, parent, all_assets) in blueprint_instances_to_spawn.iter() {
        info!("BLUEPRINT: to spawn detected: {:?} path:{:?}", blueprint_info.name, blueprint_info.path);
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
            let foo_extras = scene.extras().clone().unwrap();

            let lookup: HashMap<String, Value> = serde_json::from_str(&foo_extras.get()).unwrap();
            /*for (key, value) in lookup.clone().into_iter() {
                println!("{} / {}", key, value);
            }*/

            if lookup.contains_key("BlueprintAssets"){
                let assets_raw = &lookup["BlueprintAssets"];
                //println!("ASSETS RAW {}", assets_raw);
                let all_assets: BlueprintAssets = ron::from_str(&assets_raw.as_str().unwrap()).unwrap();
                // println!("all_assets {:?}", all_assets);

                for asset in all_assets.assets.iter() {
                    let untyped_handle = asset_server.load_untyped(&asset.path);
                    //println!("untyped handle {:?}", untyped_handle);
                    //asset_server.load(asset.path);
                    let asset_id = untyped_handle.id();
                    //println!("ID {:?}", asset_id);
                    let loaded = asset_server.is_loaded_with_dependencies(asset_id);
                    //println!("Loaded ? {:?}", loaded);
                    if !loaded {
                        asset_infos.push(AssetLoadTracker {
                            name: asset.name.clone(),
                            path: asset.path.clone(),
                            id: asset_id,
                            loaded: false,
                            handle: untyped_handle.clone(),
                        });
                    }
                }
            }
        }

        // now insert load tracker
        if !asset_infos.is_empty() {
            commands
                .entity(entity)
                .insert(BlueprintAssetsLoadState {
                    all_loaded: false,
                    asset_infos,
                    ..Default::default()
                })
                .insert(BlueprintAssetsNotLoaded)                
                ;
        } else {
            commands.entity(entity).insert(BlueprintAssetsLoaded);
        }


        commands.entity(entity).insert(BlueprintSpawning);
    }
}

pub(crate) fn blueprints_check_assets_loading(
    mut blueprint_assets_to_load: Query<
        (Entity, Option<&Name>, &BlueprintInfo, &mut BlueprintAssetsLoadState),
        With<BlueprintAssetsNotLoaded>,
    >,
    asset_server: Res<AssetServer>,
    mut commands: Commands,
    mut blueprint_events: EventWriter<BlueprintEvent>,

) {
    for (entity, entity_name, blueprint_info, mut assets_to_load) in blueprint_assets_to_load.iter_mut() {
        let mut all_loaded = true;
        let mut loaded_amount = 0;
        let total = assets_to_load.asset_infos.len();
        for tracker in assets_to_load.asset_infos.iter_mut() {
            let asset_id = tracker.id;
            let loaded = asset_server.is_loaded_with_dependencies(asset_id);
            // println!("loading {}: // load state: {:?}", tracker.name, asset_server.load_state(asset_id));

            // FIXME: hack for now
            let mut failed = false;// asset_server.load_state(asset_id) == bevy::asset::LoadState::Failed(_error);
            match asset_server.load_state(asset_id) {
                bevy::asset::LoadState::Failed(_) => {
                    failed = true
                },
                _ => {}
            }
            tracker.loaded = loaded || failed;
            if loaded || failed {
                loaded_amount += 1;
            } else {
                all_loaded = false;
            }
        }
        let progress: f32 = loaded_amount as f32 / total as f32;
        assets_to_load.progress = progress;

        if all_loaded {
            assets_to_load.all_loaded = true;
            // println!("LOADING: DONE for ALL assets of {:?} (instance of {}), preparing for spawn", entity_name, blueprint_info.path);
            // blueprint_events.send(BlueprintEvent::AssetsLoaded {blueprint_name:"".into(), blueprint_path: blueprint_info.path.clone() });

            commands
                .entity(entity)
                .insert(BlueprintAssetsLoaded)
                .remove::<BlueprintAssetsNotLoaded>()
                //.remove::<BlueprintAssetsLoadState>() //REMOVE it in release mode/ when hot reload is off, keep it for dev/hot reload
                ;
        }else {
            // println!("LOADING: in progress for ALL assets of {:?} (instance of {}): {} ",entity_name, blueprint_info.path, progress * 100.0);
        }
    }
}

/* 
pub(crate) fn hot_reload_asset_check(
    mut blueprint_assets: Query<
    (Entity, Option<&Name>, &BlueprintInfo, &mut BlueprintAssetsLoadState)>,
    asset_server: Res<AssetServer>,
    mut commands: Commands,
){
    for (entity, entity_name, blueprint_info, mut assets_to_load) in blueprint_assets.iter_mut() {
        for tracker in assets_to_load.asset_infos.iter_mut() {
            let asset_id = tracker.id;
            asset_server.is_changed()
            if asset_server.load_state(asset_id) == bevy::asset::LoadState::
            match asset_server.load_state(asset_id) {
                bevy::asset::LoadState::Failed(_) => {
                    failed = true
                },
                _ => {}
            }
        }

            //AssetEvent::Modified`
    }
    
}*/

use bevy::asset::AssetEvent;

pub(crate) fn react_to_asset_changes(
    mut gltf_events: EventReader<AssetEvent<Gltf>>,
    mut untyped_events: EventReader<AssetEvent<LoadedUntypedAsset>>,
    mut blueprint_assets: Query<(Entity, Option<&Name>, &BlueprintInfo, &mut BlueprintAssetsLoadState, Option<&Children>)>,
    asset_server: Res<AssetServer>,
    mut commands: Commands,

) {

    for event in gltf_events.read() {
        // LoadedUntypedAsset
        match event {
            AssetEvent::Modified { id } => {
                // React to the image being modified
                // println!("Modified gltf {:?}", asset_server.get_path(*id));
                for (entity, entity_name, blueprint_info, mut assets_to_load, children) in blueprint_assets.iter_mut() {
                    for tracker in assets_to_load.asset_infos.iter_mut() {
                        if asset_server.get_path(*id).is_some() {
                            if tracker.path == asset_server.get_path(*id).unwrap().to_string() {
                                println!("HOLY MOLY IT DETECTS !!, now respawn {:?}", entity_name);
                                if children.is_some() {
                                    for child in children.unwrap().iter(){
                                        commands.entity(*child).despawn_recursive();
                                    }
                                }
                                commands.entity(entity)
                                    .remove::<BlueprintAssetsLoaded>()
                                    .remove::<SceneInstance>()
                                    .remove::<BlueprintAssetsLoadState>()
                                    .insert(SpawnHere);

                                break;
                            }
                        }
                    }
                }

            }
            _ => {}
        }
    }
}



pub(crate) fn blueprints_assets_ready(spawn_placeholders: Query<
    (
        Entity,
        &BlueprintInfo,
        Option<&Transform>,
        Option<&Parent>,
        Option<&AddToGameWorld>,
        Option<&Name>,
    ),
    (
        With<BlueprintAssetsLoaded>,
        Added<BlueprintAssetsLoaded>,
        Without<BlueprintAssetsNotLoaded>,
    ),
>,

    mut commands: Commands,
    mut game_world: Query<Entity, With<GameWorldTag>>,

    assets_gltf: Res<Assets<Gltf>>,
    asset_server: Res<AssetServer>,
    children: Query<&Children>,)
{
    for (
        entity,
        blueprint_info,
        transform,
        original_parent,
        add_to_world,
        name,
    ) in spawn_placeholders.iter()
    {
        info!(
            "BLUEPRINT: all assets loaded, attempting to spawn blueprint SCENE {:?} for entity {:?}, id: {:?}, parent:{:?}",
            blueprint_info.name, name, entity, original_parent
        );

        // info!("attempting to spawn {:?}", model_path);
        let model_handle: Handle<Gltf> = asset_server.load(blueprint_info.path.clone()); // FIXME: kinda weird now

        let gltf = assets_gltf.get(&model_handle).unwrap_or_else(|| {
            panic!(
                "gltf file {:?} should have been loaded",
                &blueprint_info.path
            )
        });

        // WARNING we work under the assumtion that there is ONLY ONE named scene, and that the first one is the right one
        let main_scene_name = gltf
            .named_scenes
            .keys()
            .next()
            .expect("there should be at least one named scene in the gltf file to spawn");

        let scene = &gltf.named_scenes[main_scene_name];

        // transforms are optional, but still deal with them correctly
        let mut transforms: Transform = Transform::default();
        if transform.is_some() {
            transforms = *transform.unwrap();
        }

        let mut original_children: Vec<Entity> = vec![];
        if let Ok(c) = children.get(entity) {
            for child in c.iter() {
                original_children.push(*child);
            }
        }

        let mut named_animations:HashMap<String, Handle<AnimationClip>> = HashMap::new() ;
        for (key, value) in gltf.named_animations.iter() {
            named_animations.insert(key.to_string(), value.clone());
        }

        commands.entity(entity).insert((
            SceneBundle {
                scene: scene.clone(),
                transform: transforms,
                visibility: Visibility::Hidden,

                ..Default::default()
            },
            OriginalChildren(original_children),
            BlueprintAnimations {
                // these are animations specific to the inside of the blueprint
                named_animations: named_animations//gltf.named_animations.clone(),
            },
            
        ));

        /*        if add_to_world.is_some() {
            let world = game_world
                .get_single_mut()
                .expect("there should be a game world present");
            commands.entity(world).add_child(entity);
        } */

    }
}


#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct SubBlueprintsSpawnTracker{
    sub_blueprint_instances: HashMap<Entity, bool>
}

#[derive(Component, Reflect, Debug)]
#[reflect(Component)]
pub struct SpawnTrackRoot(Entity);

pub(crate) fn blueprints_check_blueprints_spawning(
    foo: Query<(Entity, Option<&Name>, Option<&Children>, Option<&SpawnTrackRoot>), (With<BlueprintSpawning>, Added<SceneInstance>)>,
    spawning_blueprints: Query<(Entity, Option<&Name>, Option<&Children>), Added<BlueprintSpawned>>,

    mut trackers: Query<(Entity, &mut SubBlueprintsSpawnTracker)>,
    with_blueprint_infos : Query<(Entity, Option<&Name>), With<BlueprintInfo>>,
    all_children: Query<&Children>,
    mut commands: Commands,
) {
    for (entity, name, children, track_root) in foo.iter(){
        info!("Done spawning blueprint scene for {:?} (track root: {:?})", name, track_root);
        let mut sub_blueprint_instances: Vec<Entity> = vec![];
        let mut tracker_data: HashMap<Entity, bool> = HashMap::new();

        if children.is_some() {
            //println!("has children");
            let children = children
                .expect("there should be some children of the current blueprint instance");

            for child in all_children.iter_descendants(entity) {
                if with_blueprint_infos.get(child).is_ok() {
                    sub_blueprint_instances.push(child);
                    tracker_data.insert(child, false);
                    commands.entity(child).insert(SpawnTrackRoot(entity));// Injecting to know which entity is the root
                }
            }

            /*for child in children.iter() {
                // println!("  child: {:?}", child);
                /*if with_blueprint_infos.get(*child).is_ok() {
                    sub_blueprint_instances.push(*child);
                } */

                all_children
                if let Ok(sub_children) = all_children.get(*child) {
                    for sub_child in sub_children.iter() {
                        if with_blueprint_infos.get(*sub_child).is_ok() {
                            sub_blueprint_instances.push(*sub_child);
                        }
                    }
                }
            }*/
        }
        if let Some(track_root) = track_root {
            //println!("got some root");
            if let Ok((s_entity, mut tracker)) = trackers.get_mut(track_root.0) {
                // println!("found the tracker, setting loaded for {}", entity);
                tracker.sub_blueprint_instances.entry(entity).or_insert(true);
                tracker.sub_blueprint_instances.insert(entity, true);

                // TODO: ugh, my limited rust knowledge, this is bad code
                let mut all_spawned = true;

                for key in tracker.sub_blueprint_instances.keys() {
                    let val = tracker.sub_blueprint_instances[key];
                    println!("Key: {key}, Spawned {}", val);
                }

                for val in tracker.sub_blueprint_instances.values() {
                    println!("spawned {}", val);
                    if !val {
                        all_spawned = false;
                        break;
                    }
                }
                if all_spawned {
                    println!("ALLLLL SPAAAAWNED for {}", track_root.0)
                } 
            }
        }

        println!("sub blueprint instances {:?}", sub_blueprint_instances);
        commands.entity(entity)
            .insert(SubBlueprintsSpawnTracker{sub_blueprint_instances: tracker_data.clone()});
    }
    /*for(entity, name, children) in spawning_blueprints.iter() {
        println!("checking for spawning state of sub blueprints for {:?}", name);
    }*/
}


/*
BlueprintSpawning
    - Blueprint Load Assets
    - Blueprint Assets Ready: spawn Blueprint's scene
    - Blueprint Scene Ready:
        - get list of sub Blueprints if any, inject blueprints spawn tracker
            => annoying issue with the "nested" useless root node created by blender
            => distinguish between blueprint instances inside blueprint instances vs blueprint instances inside blueprints ??
    - Blueprint sub_blueprints Ready

*/


// could be done differently, by notifying each parent of a spawning blueprint that this child is done spawning ?
// perhaps using component hooks or observers (ie , if a ComponentSpawning + Parent)
pub fn track_sub_blueprints(
    spawning_blueprints: Query<(Entity, Option<&Name>, Option<&Children>), Added<BlueprintSpawned>>
) {
    for(entity, name, children) in spawning_blueprints.iter() {
        println!("checking for spawning state of sub blueprints for {:?}", name);
    }
}


