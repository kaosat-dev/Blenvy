
use bevy::prelude::*;
use bevy_gltf_blueprints::{GameWorldTag};
use crate::{
    assets::GameAssets,
    state::{AppState, GameState, InAppRunning},
};


#[derive(Event)]
pub struct LoadRequest {
    pub path: String,
}

#[derive(Resource, Default)]
pub struct LoadRequested{
    pub path: String
}

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
pub fn foo(
    mut load_requests: EventReader<LoadRequest>,
    mut commands: Commands,

){
    for load_request in load_requests.read(){
        if load_request.path != ""{
            commands.insert_resource(LoadRequested { path: load_request.path.clone() });
        }
    }
}

pub fn load_prepare(
    mut next_app_state: ResMut<NextState<AppState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    next_app_state.set(AppState::LoadingGame);
    next_game_state.set(GameState::None);
    info!("--loading: prepare")
}


pub fn unload_world(mut commands: Commands, gameworlds: Query<Entity, With<GameWorldTag>>) {
    for e in gameworlds.iter() {
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

    println!("LOADING FROM {}", save_path);


    commands.insert_resource(AmbientLight {
        color: Color::WHITE,
        brightness: 0.2,
    });
    // here we actually spawn our game world/level
    let world = commands.spawn((
        SceneBundle {
            // note: because of this issue https://github.com/bevyengine/bevy/issues/10436, "world" is now a gltf file instead of a scene
            scene: models
                .get(game_assets.world.id())
                .expect("main level should have been loaded")
                .scenes[0]
                .clone(),
            ..default()
        },
        bevy::prelude::Name::from("world"),
        GameWorldTag,
        InAppRunning,
    )).id();

    // and we fill it with dynamic data
    let scene_data = asset_server.load(format!("scenes/{save_path}"));
    let dynamic_data = commands.spawn((
        DynamicSceneBundle {
            // Scenes are loaded just like any other asset.
            scene: scene_data,
            ..default()
        },
        bevy::prelude::Name::from("world_content"),
        // GameWorldTag,
        InAppRunning,
    ))
    .id();
    commands.entity(world).add_child(dynamic_data);
    // asset_server.reload(save_path);

    next_app_state.set(AppState::AppRunning);
    next_game_state.set(GameState::InGame);
    //info!("--loading: loaded saved scene");
}