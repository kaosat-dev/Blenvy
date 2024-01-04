pub mod saveable;
pub use saveable::*;

pub mod saving;
pub use saving::*;

pub mod loading;
pub use loading::*;

use bevy::prelude::*;
use bevy::prelude::{App, IntoSystemConfigs, Plugin};
use bevy::utils::Uuid;

//use bevy::asset::free_unused_assets_system;
//use bevy_gltf_components::GltfComponentsSet;

use bevy_gltf_blueprints::GltfBlueprintsSet;

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
pub enum LoadingSet {
    Load,
    PostLoad,
}

pub struct SaveLoadPlugin;
impl Plugin for SaveLoadPlugin {
    fn build(&self, app: &mut App) {
        app
        .register_type::<Uuid>()
        .register_type::<Saveable>()
        .register_type::<Dynamic>()
        .add_event::<SaveRequest>()
        //.add_event::<LoadRequest>()

        .configure_sets(
            Update,
            (LoadingSet::Load, LoadingSet::PostLoad)
            .chain()
            .before(GltfBlueprintsSet::Spawn)
            //.before(GltfComponentsSet::Injection)
        )

        .add_systems(PreUpdate, 
            (
                prepare_save_game,
                apply_deferred,
                save_game
            )
            .chain()
            .run_if(should_save))

        .add_systems(Update,
            (
                load_prepare,
                unload_world,
                load_game,
                //load_saved_scene,
            )
            .chain()
            .run_if(should_load) // .run_if(in_state(AppState::AppRunning))
            .in_set(LoadingSet::Load)
        )
        /* .add_systems(Update,
            (
                process_loaded_scene,
                apply_deferred,
                final_cleanup,
                apply_deferred,
                free_unused_assets_system
            )
                .chain()
                .in_set(LoadingSet::PostLoad)
            )*/

        // .add_systems(Update, bla)
      ;
    }
}
