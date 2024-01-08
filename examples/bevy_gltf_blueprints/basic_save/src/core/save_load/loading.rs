
use std::path::Path;

use bevy::{prelude::*, scene::SceneInstance};
use bevy_gltf_blueprints::{GameWorldTag, BluePrintBundle, BlueprintName};
use crate::{
    assets::GameAssets,
    state::{AppState, GameState, InAppRunning}, game::{DynamicEntitiesRoot, Flatten},
};

use super::SaveLoadConfig;


#[derive(Event)]
pub struct LoadRequest {
    pub path: String,
}

#[derive(Resource, Default)]
pub struct LoadRequested{
    pub path: String
}

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct CleanupScene;

pub fn should_load(
    mut load_requests: EventReader<LoadRequest>,
) -> bool {
    // return load_requests.len() > 0;
    let mut valid = false;
    for load_request in load_requests.read(){
        if load_request.path != ""{
            valid = true;
            break;
        }
    }
    return valid
}

pub fn load_prepare(
    mut next_app_state: ResMut<NextState<AppState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    next_app_state.set(AppState::LoadingGame);
    next_game_state.set(GameState::None);
    info!("--loading: prepare")
}


pub fn unload_world(mut commands: Commands, 
    gameworlds: Query<Entity, With<GameWorldTag>>,
    foo: Query<Entity, With<DynamicEntitiesRoot>>

) {
    for e in gameworlds.iter() {
        info!("--loading: despawn old world/level");
        commands.entity(e).despawn_recursive();
    }

    for e in foo.iter() {
        info!("--loading: despawn old world/level");
        commands.entity(e).despawn_recursive();
    }
}

pub fn load_game(
    mut commands: Commands,
    game_assets: Res<GameAssets>,
    models: Res<Assets<bevy::gltf::Gltf>>,
    asset_server: Res<AssetServer>,
    // load_request: Res<LoadRequested>,
    mut load_requests: EventReader<LoadRequest>,
    save_load_config: Res<SaveLoadConfig>,

    mut next_app_state: ResMut<NextState<AppState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
)
{
    
    info!("--loading: load static & dynamic data");
    //let save_path = load_request.path.clone();
    let mut save_path:String = "".into();
    for load_request in load_requests.read(){
        if load_request.path != ""{
            save_path = load_request.path.clone();
        }
    }

    let save_path = Path::new(&save_load_config.save_path).join(Path::new(save_path.as_str()));

    info!("LOADING FROM {:?}", save_path);

    let world_root = commands.spawn((
        bevy::prelude::Name::from("world"),
        GameWorldTag,
        InAppRunning,

        TransformBundle::default(),
        InheritedVisibility::default()

    )).id();

    let static_data = commands.spawn((
        bevy::prelude::Name::from("static"),

        BluePrintBundle {
            blueprint: BlueprintName("World".to_string()),
            transform: TransformBundle::from_transform(Transform::from_xyz(0.0, 0.0, 0.0)),
            ..Default::default()
        },

    )).id();

    // and we fill it with dynamic data
    let scene_data = asset_server.load({save_path});
    let dynamic_data = commands.spawn((
        DynamicSceneBundle {
            // Scenes are loaded just like any other asset.
            scene: scene_data,
            ..default()
        },
        bevy::prelude::Name::from("dynamic"),
        InAppRunning,
        DynamicEntitiesRoot,

        CleanupScene // we mark this scene as needing a cleanup
    ))
    .id();

    commands.entity(world_root).add_child(static_data);
    commands.entity(world_root).add_child(dynamic_data);

    next_app_state.set(AppState::AppRunning);
    next_game_state.set(GameState::InGame);
    //info!("--loading: loaded saved scene");
}

pub fn cleanup_loaded_scene(
    loaded_scenes: Query<Entity, (With<CleanupScene>,  Added<SceneInstance>, With<DynamicEntitiesRoot>)>,
    mut commands: Commands,
){
    for loaded_scene in loaded_scenes.iter(){
        info!("REMOVING SCENE");
        commands.entity(loaded_scene)
            .remove::<Handle<DynamicScene>>()
            .remove::<SceneInstance>()
            .remove::<CleanupScene>()
            ;
    }
}