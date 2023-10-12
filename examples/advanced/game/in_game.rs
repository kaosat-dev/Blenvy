use bevy::prelude::*;

use crate::{
    assets::GameAssets,
    state::{GameState, InAppRunning},
};
use bevy_gltf_blueprints::GameWorldTag;

pub fn setup_game(
    mut commands: Commands,
    game_assets: Res<GameAssets>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    println!("setting up all stuff");
    commands.insert_resource(AmbientLight {
        color: Color::WHITE,
        brightness: 0.2,
    });
    // here we actually spawn our game world/level

    commands.spawn((
        SceneBundle {
            scene: game_assets.world.clone(),
            ..default()
        },
        bevy::prelude::Name::from("world"),
        GameWorldTag,
        InAppRunning,
    ));

    next_game_state.set(GameState::InGame)
}
