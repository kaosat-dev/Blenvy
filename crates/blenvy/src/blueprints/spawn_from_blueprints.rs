use std::path::{Path, PathBuf};

use bevy::{gltf::Gltf, prelude::*, utils::hashbrown::HashMap};
use serde_json::Value;

use crate::{BlenvyAssets, BlenvyAssetsLoadState, AssetLoadTracker, BlenvyConfig, BlueprintAnimations, BlueprintAssetsLoaded, BlueprintAssetsNotLoaded};

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
        blueprint_name: String,
        blueprint_path: String,
        // TODO: add assets list ?
    },
    /// event fired when a blueprint is COMPLETELY done spawning ie
    /// - all its assets have been loaded
    /// - the spawning attempt has been sucessfull
    Spawned {
        blueprint_name: String,
        blueprint_path: String,
    },

    /// 
    Ready {
        blueprint_path: String,
    }
    
}


use gltf::Gltf as RawGltf;

pub(crate) fn blueprints_prepare_spawn(
    blueprint_instances_to_spawn : Query<
    (
        Entity,
        &BlueprintInfo,
        Option<&Parent>,
        Option<&BlenvyAssets>,
    ),(Added<BlueprintInfo>)
    >,
mut commands: Commands,
asset_server: Res<AssetServer>,


) {
   
    for (entity, blueprint_info, parent, all_assets) in blueprint_instances_to_spawn.iter() {
        println!("Detected blueprint to spawn {:?} {:?}", blueprint_info.name, blueprint_info.path);
        println!("all assets {:?}", all_assets);
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
                id: asset_id,
                loaded: false,
                handle: untyped_handle.clone(),
            });
        }

        // and we also add all its assets
        /* prefetch attempt */
        let gltf = RawGltf::open(format!("assets/{}", blueprint_info.path)).unwrap();// RawGltf::open("examples/Box.gltf")?;
        for scene in gltf.scenes() {
            let foo_extras = scene.extras().clone().unwrap();

            let lookup: HashMap<String, Value> = serde_json::from_str(&foo_extras.get()).unwrap();
            /*for (key, value) in lookup.clone().into_iter() {
                println!("{} / {}", key, value);
            }*/

            if lookup.contains_key("BlenvyAssets"){
                let assets_raw = &lookup["BlenvyAssets"];
                //println!("ASSETS RAW {}", assets_raw);
                let all_assets: BlenvyAssets = ron::from_str(&assets_raw.as_str().unwrap()).unwrap();
                println!("all_assets {:?}", all_assets);

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
                .insert(BlenvyAssetsLoadState {
                    all_loaded: false,
                    asset_infos,
                    ..Default::default()
                })
                .insert(BlueprintAssetsNotLoaded);
        } else {
            commands.entity(entity).insert(BlueprintAssetsLoaded);
        }
    }
}

pub(crate) fn blueprints_check_assets_loading(
    mut blueprint_assets_to_load: Query<
        (Entity, Option<&Name>, &BlueprintInfo, &mut BlenvyAssetsLoadState),
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
            println!("LOADING: in progress for ALL assets of {:?} (instance of {}), preparing for spawn", entity_name, blueprint_info.path);
            blueprint_events.send(BlueprintEvent::AssetsLoaded {blueprint_name:"".into(), blueprint_path: blueprint_info.path.clone() });

            commands
                .entity(entity)
                .insert(BlueprintAssetsLoaded)
                .remove::<BlueprintAssetsNotLoaded>()
                .remove::<BlenvyAssetsLoadState>()
                ;
        }else {
            println!("LOADING: done for ALL assets of {:?} (instance of {}): {} ",entity_name, blueprint_info.path, progress * 100.0);
        }
    }
}



pub(crate) fn blueprints_spawn(
    spawn_placeholders: Query<
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
    children: Query<&Children>,
) {
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
            "all assets loaded, attempting to spawn blueprint {:?} for entity {:?}, id: {:?}, parent:{:?}",
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
                ..Default::default()
            },
            Spawned,
            BlueprintInstanceReady, // FIXME: not sure if this is should be added here or in the post process
            OriginalChildren(original_children),
            BlueprintAnimations {
                // these are animations specific to the inside of the blueprint
                named_animations: named_animations//gltf.named_animations.clone(),
            },
        ));

        if add_to_world.is_some() {
            let world = game_world
                .get_single_mut()
                .expect("there should be a game world present");
            commands.entity(world).add_child(entity);
        }
    }
}





