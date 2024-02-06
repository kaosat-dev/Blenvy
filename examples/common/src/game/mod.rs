/*pub mod in_game;
pub use in_game::*;

pub mod in_main_menu;
pub use in_main_menu::*;*/

pub mod player;
pub use player::*;

pub mod picking;
pub use picking::*;

/* 
use crate::{
    state::{AppState, GameState},
};*/
use bevy::prelude::*;


pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((
            PlayerPlugin,
            PickingPlugin

        ))
            /* .register_type::<Interactible>()
            .register_type::<SoundMaterial>()
            .register_type::<Player>()
           
            .add_systems(OnEnter(AppState::MenuRunning), setup_main_menu)
            .add_systems(OnExit(AppState::MenuRunning), teardown_main_menu)
            .add_systems(Update, main_menu.run_if(in_state(AppState::MenuRunning)))
            .add_systems(OnEnter(AppState::AppRunning), setup_game);*/
        ;
    }
}
