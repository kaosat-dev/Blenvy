pub mod in_game;
use std::{
    fs::{self},
    time::Duration,
};

use bevy_gltf_blueprints::AnimationPlayerLink;
pub use in_game::*;

use bevy::{prelude::*, time::common_conditions::on_timer};
use bevy_gltf_worlflow_examples_common::{AppState, GameState};

fn start_game(mut next_app_state: ResMut<NextState<AppState>>) {
    next_app_state.set(AppState::AppLoading);
}

// if the export from Blender worked correctly, we should have animations (simplified here by using AnimationPlayerLink)
fn check_for_animation(animation_player_links: Query<(Entity, &AnimationPlayerLink)>) {
    let animations_found = !animation_player_links.is_empty();
    if animations_found {
        fs::write(
            "bevy_diagnostics.json",
            format!("{{ \"animations\": {} }}", animations_found),
        )
        .expect("Unable to write file");
    }
}

fn exit_game(mut app_exit_events: ResMut<Events<bevy::app::AppExit>>) {
    app_exit_events.send(bevy::app::AppExit);
}

pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Update, (spawn_test).run_if(in_state(GameState::InGame)))
            .add_systems(Update, check_for_animation)
            .add_systems(OnEnter(AppState::MenuRunning), start_game)
            .add_systems(OnEnter(AppState::AppRunning), setup_game)
            .add_systems(
                Update,
                exit_game.run_if(on_timer(Duration::from_secs_f32(0.5))),
            ) // shut down the app after this time
            ;
    }
}
