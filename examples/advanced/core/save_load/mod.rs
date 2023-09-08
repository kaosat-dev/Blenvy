pub mod saveable;
use bevy::asset::free_unused_assets_system;
use bevy_gltf_components::GltfComponentsSet;
pub use saveable::*;

pub mod saving;
pub use saving::*;

pub mod loading;
pub use loading::*;

use bevy::prelude::*;
use bevy::prelude::{App, Plugin, IntoSystemConfigs};
use bevy::utils::Uuid;

use super::blueprints::SpawnSet;



#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
pub enum LoadingSet{
  Load,
  PostLoad, 
}

pub struct SaveLoadPlugin;
impl Plugin for SaveLoadPlugin {
  fn build(&self, app: &mut App) {
      app
        .register_type::<Uuid>()
        .register_type::<Saveable>()

        .configure_sets(
            Update,
            (LoadingSet::Load, LoadingSet::PostLoad)
            .chain()
            .before(SpawnSet::Spawn)
            .before(GltfComponentsSet::Injection)
        )

        .add_systems(PreUpdate, save_game.run_if(should_save))

        .add_systems(Update, 
            (
                load_prepare,
                unload_world,
                load_world,
                load_saved_scene,
                // process_loaded_scene
            )
            .chain()
            .run_if(should_load) // .run_if(in_state(AppState::AppRunning))
            .in_set(LoadingSet::Load)
        )
         .add_systems(Update,
            (
                process_loaded_scene,
                apply_deferred,
                final_cleanup,
                apply_deferred,
                free_unused_assets_system
            )
                .chain()
                .in_set(LoadingSet::PostLoad)
            )

        
      ;
  }
}
