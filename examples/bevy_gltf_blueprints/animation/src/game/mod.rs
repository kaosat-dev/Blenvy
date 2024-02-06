pub mod in_game;
pub use in_game::*;

pub mod in_main_menu;
pub use in_main_menu::*;

use bevy::prelude::*;
use bevy_gltf_worlflow_examples_common::{AppState, GameState};

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Fox;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Robot;


pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app
            .register_type::<Robot>()
            .register_type::<Fox>()
            // little helper utility, to automatically inject components that are dependant on an other component
            // ie, here an Entity with a Player component should also always have a ShouldBeWithPlayer component
            // you get a warning if you use this, as I consider this to be stop-gap solution (usually you should have either a bundle, or directly define all needed components)
            .add_systems(
                Update,
                (
                    spawn_test,
                    animation_control,
                    animation_change_on_proximity_foxes,
                    animation_change_on_proximity_robots,
                )
                    .run_if(in_state(GameState::InGame)),
            )
            .add_systems(OnEnter(AppState::MenuRunning), setup_main_menu)
            .add_systems(OnExit(AppState::MenuRunning), teardown_main_menu)
            .add_systems(Update, main_menu.run_if(in_state(AppState::MenuRunning)))
            .add_systems(OnEnter(AppState::AppRunning), setup_game);
    }
}
