use std::path::{Path, PathBuf};

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
/// FlagComponent for dynamically spawned scenes
pub struct Spawned;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component marking any spwaned child of blueprints ..unless the original entity was marked with the 'NoInBlueprint' marker component
pub struct InBlueprint;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component preventing any spwaned child of blueprints to be marked with the InBlueprint component
pub struct NoInBlueprint;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
// this allows overriding the default library path for a given entity/blueprint
pub struct Library(pub PathBuf);

#[derive(Component)]
/// helper component, just to transfer child data
pub(crate) struct OriginalChildren(pub Vec<Entity>);


/// main spawning functions,
/// * also takes into account the already exisiting "override" components, ie "override components" > components from blueprint
pub(crate) fn spawn_from_blueprints(
    spawn_placeholders: Query<
        (
            Entity,
            &BlueprintName,
            Option<&Transform>,
            Option<&Parent>,
            Option<&Library>,
            Option<&Name>,
        ),
        (Added<BlueprintName>, Added<SpawnHere>, Without<Spawned>),
    >,

    mut commands: Commands,
    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,

    assets_gltf: Res<Assets<Gltf>>,
    asset_server: Res<AssetServer>,
    blueprints_config: Res<BluePrintsConfig>,

    children: Query<(&Children)>,
) {
    for (entity, blupeprint_name, transform, original_parent, library_override, name) in spawn_placeholders.iter() {
        info!(
            "need to spawn {:?} for entity {:?}, id: {:?}, parent:{:?}",
            blupeprint_name.0, name, entity, original_parent
        );

        let mut original_children: Vec<Entity> = vec![];
        if let Ok(c) = children.get(entity) {
            for child in c.iter() {
                original_children.push(*child);
            }
        }

        let what = &blupeprint_name.0;
        let model_file_name = format!("{}.{}", &what, &blueprints_config.format);

        let library_path = library_override.map_or_else(|| &blueprints_config.library_folder, |l| &l.0 );
        println!("LIBRARY PATH {:?}", library_path);
        // 
        let model_path =
            Path::new(&library_path).join(Path::new(model_file_name.as_str()));

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

        // transforms are optional, but still deal with them correctly
        let mut transforms: Transform = Transform::default();
        if transform.is_some() {
            transforms = transform.unwrap().clone();
        }

        commands.entity(entity).insert((
            SceneBundle {
                scene: scene.clone(),
                transform: transforms,
                ..Default::default()
            },
            Animations {
                named_animations: gltf.named_animations.clone(),
            },
            Spawned,
            OriginalChildren(original_children),
        ));

        // let world = game_world.single_mut();
        // let mut parent = world.1[0]; // FIXME: dangerous hack because our gltf data have a single child like this, but might not always be the case

        // ideally, insert the newly created entity as a child of the original parent, if any, the world otherwise
        if let Some(original_parent) = original_parent {
            // parent = original_parent.get();
        }

        // commands.entity(parent).add_child(entity);
    }
}
