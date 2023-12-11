use std::path::Path;

use bevy::{gltf::Gltf, prelude::*};

use crate::{Animations, BluePrintsConfig};

/// this is a flag component for our levels/game world
#[derive(Component)]
pub struct GameWorldTag;

/// Main component for the blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct BlueprintName(pub String);

/// flag component needed to signify the intent to spawn a Blueprint
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct SpawnHere;

#[derive(Component)]
/// FlagComponent for spawned entity
pub struct Spawned;

#[derive(Component)]
/// helper component, just to transfer some data
pub(crate) struct Original(pub Entity);

#[derive(Component)]
/// FlagComponent for dynamically spawned scenes
pub struct SpawnedRoot;

/// main spawning functions,
/// * also takes into account the already exisiting "override" components, ie "override components" > components from blueprint
pub(crate) fn spawn_from_blueprints(
    spawn_placeholders: Query<
        (Entity, &Name, &BlueprintName, &Transform),
        (
            Added<BlueprintName>,
            Added<SpawnHere>,
            Without<Spawned>,
            Without<SpawnedRoot>,
        ),
    >,

    mut commands: Commands,
    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,

    assets_gltf: Res<Assets<Gltf>>,
    asset_server: Res<AssetServer>,
    blueprints_config: Res<BluePrintsConfig>,
) {
    for (entity, name, blupeprint_name, transform) in spawn_placeholders.iter() {
        debug!("need to spawn {:?}", blupeprint_name.0);
        let what = &blupeprint_name.0;
        let model_file_name = format!("{}.{}", &what, &blueprints_config.format);
        let model_path =
            Path::new(&blueprints_config.library_folder).join(Path::new(model_file_name.as_str()));

        debug!("attempting to spawn {:?}", model_path);
        let model_handle: Handle<Gltf> = asset_server.load(model_path);

        let world = game_world.single_mut();
        let world = world.1[0]; // FIXME: dangerous hack because our gltf data have a single child like this, but might not always be the case

        let gltf = assets_gltf
            .get(&model_handle)
            .expect("this gltf should have been loaded");

        let foo = gltf.named_materials.clone();
        println!("Materials {:?}", foo);

        // WARNING we work under the assumtion that there is ONLY ONE named scene, and that the first one is the right one
        let main_scene_name = gltf
            .named_scenes
            .keys()
            .nth(0)
            .expect("there should be at least one named scene in the gltf file to spawn");
        let scene = &gltf.named_scenes[main_scene_name];

        let child_scene = commands
            .spawn((
                SceneBundle {
                    scene: scene.clone(),
                    transform: transform.clone(),
                    ..Default::default()
                },
                name.clone(),
                // Parent(world) // FIXME/ would be good if this worked directly
                SpawnedRoot,
                BlueprintName(blupeprint_name.0.clone()),
                Original(entity),
                Animations {
                    named_animations: gltf.named_animations.clone(),
                },
            ))
            .id();
        commands.entity(world).add_child(child_scene);
    }
}
