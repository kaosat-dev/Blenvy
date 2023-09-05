pub mod saveable;
pub use saveable::*;

pub mod saving;
pub use saving::*;

pub mod loading;
pub use loading::*;

use bevy::prelude::*;
use bevy::prelude::{App, Plugin, IntoSystemConfigs};
use bevy::utils::Uuid;

pub struct SaveLoadPlugin;
impl Plugin for SaveLoadPlugin {
  fn build(&self, app: &mut App) {
      app
        .register_type::<Uuid>()
        .register_type::<Saveable>()

        .add_systems(PreUpdate, save_game.run_if(should_save))

        .add_systems(Update, 

            (
                unload_world,
                load_world,
                load_saved_scene,
                // process_loaded_scene
            )
            .chain()
            .run_if(should_load) // .run_if(in_state(AppState::GameRunning))
        )
         .add_systems(Update,
            (
                process_loaded_scene,
                final_cleanup
            ).chain()
        )
      ;
  }
}
