use std::path::Path;

use bevy::{prelude::*, scene::SceneInstance};
use bevy_gltf_blueprints::{BluePrintBundle, BlueprintName, GameWorldTag};

use crate::{DynamicEntitiesRoot, StaticEntitiesRoot};

use super::{Dynamic, SaveLoadConfig};

#[derive(Event)]
pub struct LoadRequest {
    pub path: String,
}

#[derive(Event)]
pub struct LoadingFinished;



#[derive(Resource, Default)]
pub struct LoadRequested {
    pub path: String,
}

#[derive(Resource, Default)]
pub(crate) struct LoadFirstStageDone;

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct CleanupScene;

pub(crate) fn should_load() -> bool {
  
    return true
}

pub(crate) fn mark_load_requested(
    mut load_requests: EventReader<LoadRequest>,
    mut commands: Commands
){
    let mut save_path: String = "".into();
    for load_request in load_requests.read() {
        if load_request.path != "" {
            save_path = load_request.path.clone();
        }
    }
    if save_path!= "" {
        commands.insert_resource(LoadRequested{path: save_path});
    }
}

// TODO: replace with generic despawner ?
pub(crate) fn unload_world(mut commands: Commands, gameworlds: Query<Entity, With<GameWorldTag>>) {
    for e in gameworlds.iter() {
        info!("--loading: despawn old world/level");
        commands.entity(e).despawn_recursive();
    }
}

pub fn load_game(
    mut commands: Commands,
    models: Res<Assets<bevy::gltf::Gltf>>,
    asset_server: Res<AssetServer>,
    load_request: Res<LoadRequested>,
    save_load_config: Res<SaveLoadConfig>,
) {
    info!("--loading: load dynamic data");
    let save_path = load_request.path.clone();
    let save_path = Path::new(&save_load_config.save_path).join(Path::new(save_path.as_str()));

    info!("LOADING FROM {:?}", save_path);

    let world_root = commands
        .spawn((
            bevy::prelude::Name::from("world"),
            GameWorldTag,
            TransformBundle::default(),
            InheritedVisibility::default(),
        ))
        .id();

    // and we fill it with dynamic data
    // let input = std::fs::read(&path)?;
    let dynamic_data = commands
        .spawn((
            DynamicSceneBundle {
                // Scenes are loaded just like any other asset.
                scene: asset_server.load(save_path),
                ..default()
            },
            bevy::prelude::Name::from("dynamic"),
            DynamicEntitiesRoot,
        ))
        .id();

    // commands.entity(world_root).add_child(static_data);
    commands.entity(world_root).add_child(dynamic_data);

    commands.insert_resource(LoadFirstStageDone);

    info!("--loading: loaded dynamic data");
}

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct TestMarker;

pub fn load_static(
    dynamic_worlds: Query<Entity, With<SceneInstance>>,
    static_worlds: Query<(Entity, &StaticEntitiesRoot), (Added<StaticEntitiesRoot>)>,
    world_root: Query<(Entity), With<GameWorldTag>>,
    mut commands: Commands,
    mut loading_finished: EventWriter<LoadingFinished>,
) {
 
    for (entity, marker) in static_worlds.iter() {
        info!("--loading static data {:?}", marker.0);

        let static_data = commands
            .spawn((
                bevy::prelude::Name::from("static"),
                BluePrintBundle {
                    blueprint: BlueprintName(marker.0.clone()),
                    ..Default::default()
                },
            ))
            .id();

        let world_root = world_root.get_single().unwrap();
        println!("root {:?}", world_root);
        commands.entity(world_root).add_child(static_data);
        
        info!("--loading: loaded static data");
        for (entity) in dynamic_worlds.iter() {
            commands.entity(entity).insert(
                CleanupScene, // we mark this scene as needing a cleanup
            );
        }

        loading_finished.send(LoadingFinished);
        break;
    }
   
}

pub fn cleanup_loaded_scene(
    loaded_scenes: Query<
        Entity,
        (
            Added<CleanupScene>,
            With<SceneInstance>,
            With<DynamicEntitiesRoot>,
        ),
    >,
    mut commands: Commands,
) {
    for loaded_scene in loaded_scenes.iter() {
        info!("REMOVING DynamicScene");
        commands
            .entity(loaded_scene)
            .remove::<Handle<DynamicScene>>()
            .remove::<SceneInstance>()
            .remove::<CleanupScene>();

        commands.remove_resource::<LoadRequested>();
        commands.remove_resource::<LoadFirstStageDone>();

    }
}
