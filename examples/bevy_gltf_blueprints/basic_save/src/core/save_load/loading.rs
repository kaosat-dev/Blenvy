
use bevy::prelude::*;
use bevy_gltf_blueprints::{clone_entity::CloneEntity, GameWorldTag, SpawnHere};
use crate::{
    assets::GameAssets,
    state::{AppState, GameState, InAppRunning},
};

const SCENE_FILE_PATH: &str = "scenes/save.scn.ron";


pub fn should_load(
    keycode: Res<Input<KeyCode>>,
   //save_requested_events: EventReader<SaveRequest>,
) -> bool {
   //return save_requested_events.len() > 0;

   return keycode.just_pressed(KeyCode::L)
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
    mut next_game_state: ResMut<NextState<GameState>>,
    asset_server: Res<AssetServer>,

)
{

    println!("LOADING setting up all stuff");
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
    let dynamic_data = commands.spawn((
        DynamicSceneBundle {
            // Scenes are loaded just like any other asset.
            scene: asset_server.load(SCENE_FILE_PATH),
            ..default()
        },
        bevy::prelude::Name::from("world_content"),
        // GameWorldTag,
        InAppRunning,
    ))
    .id();
    commands.entity(world).add_child(dynamic_data);

    next_game_state.set(GameState::InGame)

    //info!("--loading: loaded saved scene");
}