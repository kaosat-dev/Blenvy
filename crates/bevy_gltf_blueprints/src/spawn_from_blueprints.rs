use std::path::{Path, PathBuf};

use bevy::{gltf::Gltf, prelude::*, utils::hashbrown::HashMap};

use crate::{
    AssetLoadTracker, AssetsToLoad, BluePrintsConfig, BlueprintAnimations, BlueprintAssets,
    BlueprintAssetsLoaded, BlueprintAssetsNotLoaded,
};

/// this is a flag component for our levels/game world
#[derive(Component)]
pub struct GameWorldTag;

/// Main component for the blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct BlueprintName(pub String);

/// path component for the blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct BlueprintPath(pub String);

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

pub(crate) fn test_thingy(
    spawn_placeholders: Query<
        (Entity, &BlueprintPath),
        (Added<BlueprintPath>, Without<Spawned>, Without<SpawnHere>),
    >,

    // before 0.14 we have to use a seperate query, after migrating we can query at the root level
    entities_with_assets: Query<
        (
            Entity,
            /*&BlueprintName,
            &BlueprintPath,
            Option<&Parent>,*/
            Option<&Name>,
            Option<&BlueprintAssets>,
        ),
        (Added<BlueprintAssets>), //  Added<BlueprintAssets>
    >,

    bla_bla: Query<
        (Entity, &BlueprintName, &BlueprintPath, Option<&Parent>),
        (Added<BlueprintPath>),
    >,
    mut commands: Commands,
    asset_server: Res<AssetServer>,
) {
    for (entity, blueprint_path) in spawn_placeholders.iter() {
        //println!("added blueprint_path {:?}", blueprint_path);
        /*commands.entity(entity).insert(
            SceneBundle {
                scene: asset_server.load(format!("{}#Scene0", &blueprint_path.0)), // "levels/World.glb#Scene0"),
                ..default()
            },
        );*/
        // let model_handle: Handle<Gltf> = asset_server.load(model_path.clone());
    }

    for (entity, blueprint_name, blueprint_path, parent) in bla_bla.iter() {
        println!(
            "added blueprint to spawn {:?} {:?}",
            blueprint_name, blueprint_path
        );
        let untyped_handle = asset_server.load_untyped(&blueprint_path.0);
        let asset_id = untyped_handle.id();
        let loaded = asset_server.is_loaded_with_dependencies(asset_id);

        let mut asset_infos: Vec<AssetLoadTracker> = vec![];
        if !loaded {
            asset_infos.push(AssetLoadTracker {
                name: blueprint_name.0.clone(),
                id: asset_id,
                loaded: false,
                handle: untyped_handle.clone(),
            });
        }

        // now insert load tracker
        if !asset_infos.is_empty() {
            commands
                .entity(entity)
                .insert(AssetsToLoad {
                    all_loaded: false,
                    asset_infos,
                    ..Default::default()
                })
                .insert(BlueprintAssetsNotLoaded);
        } else {
            commands.entity(entity).insert(BlueprintAssetsLoaded);
        }
    }

    for (child_entity, child_entity_name, all_assets) in entities_with_assets.iter() {
        println!("added assets {:?} to {:?}", all_assets, child_entity_name);
        if all_assets.is_some() {
            let mut asset_infos: Vec<AssetLoadTracker> = vec![];

            for asset in all_assets.unwrap().0.iter() {
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

            // now insert load tracker
            if !asset_infos.is_empty() {
                commands
                    .entity(child_entity)
                    .insert(AssetsToLoad {
                        all_loaded: false,
                        asset_infos,
                        ..Default::default()
                    })
                    .insert(BlueprintAssetsNotLoaded);
            } else {
                commands.entity(child_entity).insert(BlueprintAssetsLoaded);
            }
        }
    }
}

pub(crate) fn check_for_loaded2(
    mut blueprint_assets_to_load: Query<
        (Entity, Option<&Name>, &mut AssetsToLoad),
        With<BlueprintAssetsNotLoaded>,
    >,
    asset_server: Res<AssetServer>,
    mut commands: Commands,
) {
    for (entity, entity_name, mut assets_to_load) in blueprint_assets_to_load.iter_mut() {
        let mut all_loaded = true;
        let mut loaded_amount = 0;
        let total = assets_to_load.asset_infos.len();
        for tracker in assets_to_load.asset_infos.iter_mut() {
            let asset_id = tracker.id;
            let loaded = asset_server.is_loaded_with_dependencies(asset_id);
            println!(
                "loading {}: // load state: {:?}",
                tracker.name,
                asset_server.load_state(asset_id)
            );

            // FIXME: hack for now
            let mut failed = false; // asset_server.load_state(asset_id) == bevy::asset::LoadState::Failed(_error);
            match asset_server.load_state(asset_id) {
                bevy::asset::LoadState::Failed(_) => failed = true,
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
        println!("progress: {}", progress);
        assets_to_load.progress = progress;

        if all_loaded {
            assets_to_load.all_loaded = true;
            println!("done with loading {:?}, inserting components", entity_name);
            commands
                .entity(entity)
                .insert(BlueprintAssetsLoaded)
                .remove::<BlueprintAssetsNotLoaded>()
                .remove::<AssetsToLoad>();
        }
    }
}

pub(crate) fn spawn_from_blueprints2(
    spawn_placeholders: Query<
        (
            Entity,
            &BlueprintName,
            &BlueprintPath,
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
    blueprints_config: Res<BluePrintsConfig>,

    children: Query<&Children>,
) {
    for (entity, blupeprint_name, blueprint_path, transform, original_parent, add_to_world, name) in
        spawn_placeholders.iter()
    {
        info!(
            "attempting to spawn blueprint {:?} for entity {:?}, id: {:?}, parent:{:?}",
            blupeprint_name.0, name, entity, original_parent
        );

        // info!("attempting to spawn {:?}", model_path);
        let model_handle: Handle<Gltf> = asset_server.load(blueprint_path.0.clone()); // FIXME: kinda weird now

        let gltf = assets_gltf
            .get(&model_handle)
            .unwrap_or_else(|| panic!("gltf file {:?} should have been loaded", &blueprint_path.0));

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

        let mut named_animations: HashMap<String, Handle<AnimationClip>> = HashMap::new();
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
                named_animations: named_animations, //gltf.named_animations.clone(),
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
