pub mod in_game;
pub use in_game::*;

use bevy::prelude::*;
use bevy_gltf_worlflow_examples_common::{AppState, GameState};


fn start_game(
    mut next_app_state: ResMut<NextState<AppState>>,
){
    next_app_state.set(AppState::AppLoading);
}
pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(
            Update,
            (spawn_test).run_if(in_state(GameState::InGame)),
        )
        .add_systems(OnEnter(AppState::MenuRunning), start_game)
        .add_systems(OnEnter(AppState::AppRunning), setup_game);
    }
}
