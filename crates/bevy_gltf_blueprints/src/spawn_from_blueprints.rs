use std::path::Path;

use bevy::{gltf::Gltf, prelude::*};

use crate::{Animations, BluePrintsConfig, EntityMapper};

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
/// helper component, just to transfer child data
pub(crate) struct OriginalChildren(pub Vec<Entity>);

#[derive(Component)]
/// FlagComponent for dynamically spawned scenes
pub struct SpawnedRoot;

/// main spawning functions,
/// * also takes into account the already exisiting "override" components, ie "override components" > components from blueprint
pub(crate) fn spawn_from_blueprints(
    spawn_placeholders: Query<
        (Entity, &Name, &BlueprintName, &Transform, Option<&Parent>),
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

    children: Query<(&Children)>,
    names: Query<&Name>,
    mut mappings: ResMut<EntityMapper>

) {
    for (entity, name, blupeprint_name, transform, original_parent) in spawn_placeholders.iter() {
        info!("need to spawn {:?} for entity {:?}, id: {:?}", blupeprint_name.0, name, entity);

        let mut original_children: Vec<Entity> = vec![];
        if let Ok(c) = children.get(entity) {
            for child in c.iter() {
                info!("--child {:?} {:?} of {:?}", names.get(*child), child, name);
                original_children.push(*child);
            }
        }

        let what = &blupeprint_name.0;
        let model_file_name = format!("{}.{}", &what, &blueprints_config.format);
        let model_path =
            Path::new(&blueprints_config.library_folder).join(Path::new(model_file_name.as_str()));

        debug!("attempting to spawn {:?}", model_path);
        let model_handle: Handle<Gltf> = asset_server.load(model_path);

        let gltf = assets_gltf
            .get(&model_handle)
            .expect("this gltf should have been loaded");

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
                OriginalChildren(original_children),
                Animations {
                    named_animations: gltf.named_animations.clone(),
                },
            ))
            .id();

        let world = game_world.single_mut();
        let mut parent = world.1[0]; // FIXME: dangerous hack because our gltf data have a single child like this, but might not always be the case

        // ideally, insert the newly created entity as a child of the original parent, if any, the world otherwise
        if let Some(original_parent) = original_parent {
            // println!("here");
            /*let mut real_parent = original_parent.get();
            if let Some(p) = mappings.map.get(&original_parent.get()) {
                real_parent = p;
                println!("MAPPING")
            } */
            parent = original_parent.get();
        }

        commands.entity(parent).add_child(child_scene);
    }
}
