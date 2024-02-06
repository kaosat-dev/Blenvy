pub mod state;
pub use state::*;

pub mod assets;
use assets::*;

pub mod core;
pub use core::*;

pub mod game;
pub use game::*;

use bevy::prelude::*;

pub struct CommonPlugin;
impl Plugin for CommonPlugin {
    fn build(&self, app: &mut App) {
        app
            .add_plugins((
                StatePlugin,
                AssetsPlugin,
                CorePlugin,
                GamePlugin
            ));
         
    }
}
