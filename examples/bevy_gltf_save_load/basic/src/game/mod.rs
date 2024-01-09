pub mod in_game;
pub use in_game::*;

pub mod in_main_menu;
pub use in_main_menu::*;

pub mod in_game_loading;
pub use in_game_loading::*;

pub mod in_game_saving;
pub use in_game_saving::*;

pub mod picking;
pub use picking::*;

use crate::{
    insert_dependant_component,
    state::{AppState, GameState},
};
use bevy::prelude::*;
use bevy_gltf_save_load::{LoadRequest, LoadingFinished, SaveRequest, SavingFinished};
use bevy_rapier3d::prelude::*;

// this file is just for demo purposes, contains various types of components, systems etc

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub enum SoundMaterial {
    Metal,
    Wood,
    Rock,
    Cloth,
    Squishy,
    #[default]
    None,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Player;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo component showing auto injection of components
pub struct ShouldBeWithPlayer;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Interactible;

fn player_move_demo(
    keycode: Res<Input<KeyCode>>,
    mut players: Query<&mut Transform, With<Player>>,
) {
    let speed = 0.2;
    if let Ok(mut player) = players.get_single_mut() {
        if keycode.pressed(KeyCode::Left) {
            player.translation.x += speed;
        }
        if keycode.pressed(KeyCode::Right) {
            player.translation.x -= speed;
        }

        if keycode.pressed(KeyCode::Up) {
            player.translation.z += speed;
        }
        if keycode.pressed(KeyCode::Down) {
            player.translation.z -= speed;
        }
    }
}

pub fn request_save(
    mut save_requests: EventWriter<SaveRequest>,
    keycode: Res<Input<KeyCode>>,

    current_state: Res<State<GameState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    if keycode.just_pressed(KeyCode::S)
        && (current_state.get() != &GameState::InLoading)
        && (current_state.get() != &GameState::InSaving)
    {
        next_game_state.set(GameState::InSaving);
        save_requests.send(SaveRequest {
            path: "save.scn.ron".into(),
        })
    }
}

pub fn on_saving_finished(
    mut saving_finished: EventReader<SavingFinished>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    for _ in saving_finished.read() {
        next_game_state.set(GameState::InGame);
    }
}

pub fn request_load(
    mut load_requests: EventWriter<LoadRequest>,
    keycode: Res<Input<KeyCode>>,
    current_state: Res<State<GameState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    if keycode.just_pressed(KeyCode::L)
        && (current_state.get() != &GameState::InLoading)
        && (current_state.get() != &GameState::InSaving)
    {
        next_game_state.set(GameState::InLoading);
        load_requests.send(LoadRequest {
            path: "save.scn.ron".into(),
        })
    }
}

pub fn on_loading_finished(
    mut loading_finished: EventReader<LoadingFinished>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    for _ in loading_finished.read() {
        next_game_state.set(GameState::InGame);
    }
}

pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins(PickingPlugin)
            .register_type::<Interactible>()
            .register_type::<SoundMaterial>()
            .register_type::<Player>()
            .add_systems(
                Update,
                (
                    // little helper utility, to automatically inject components that are dependant on an other component
                    // ie, here an Entity with a Player component should also always have a ShouldBeWithPlayer component
                    // you get a warning if you use this, as I consider this to be stop-gap solution (usually you should have either a bundle, or directly define all needed components)

                    // insert_dependant_component::<Player, ShouldBeWithPlayer>,
                    player_move_demo, //.run_if(in_state(AppState::Running)),
                    spawn_test,
                    spawn_test_unregisted_components,
                    spawn_test_parenting,
                )
                    .run_if(in_state(GameState::InGame)),
            )
            .add_systems(
                Update,
                (unload_world, apply_deferred, setup_game)
                    .chain()
                    .run_if(should_reset)
                    .run_if(in_state(AppState::AppRunning)),
            )
            .add_systems(
                Update,
                (
                    request_save,
                    request_load,
                    on_saving_finished,
                    on_loading_finished,
                ),
            )
            .add_systems(OnEnter(AppState::MenuRunning), setup_main_menu)
            .add_systems(OnExit(AppState::MenuRunning), teardown_main_menu)
            .add_systems(Update, main_menu.run_if(in_state(AppState::MenuRunning)))
            .add_systems(OnEnter(GameState::InLoading), setup_loading_screen)
            .add_systems(OnExit(GameState::InLoading), teardown_loading_screen)
            .add_systems(OnEnter(GameState::InSaving), setup_saving_screen)
            .add_systems(OnExit(GameState::InSaving), teardown_saving_screen)
            .add_systems(OnEnter(AppState::AppRunning), setup_game);
    }
}
