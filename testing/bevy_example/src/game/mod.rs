pub mod in_game;
use std::time::Duration;

pub use in_game::*;

use bevy::{prelude::*, time::common_conditions::on_timer};
use bevy_gltf_worlflow_examples_common::{AppState, GameState};


fn start_game(
    mut next_app_state: ResMut<NextState<AppState>>,
){
    next_app_state.set(AppState::AppLoading);
}

fn exit_game(mut app_exit_events: ResMut<Events<bevy::app::AppExit>>) {
    app_exit_events.send(bevy::app::AppExit);
}

pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(
            Update,
            (spawn_test).run_if(in_state(GameState::InGame)),
        )
        .add_systems(OnEnter(AppState::MenuRunning), start_game)
        .add_systems(Update, exit_game.run_if(on_timer(Duration::from_secs_f32(0.5)))) // shut down the app after this time
        .add_systems(OnEnter(AppState::AppRunning), setup_game);
    }
}
