pub mod saveable;
use std::path::PathBuf;

pub use saveable::*;

pub mod saving;
pub use saving::*;

pub mod loading;
pub use loading::*;

use bevy::core_pipeline::core_3d::{Camera3dDepthTextureUsage, ScreenSpaceTransmissionQuality};
use bevy::prelude::*;
use bevy::prelude::{App, IntoSystemConfigs, Plugin};
use bevy_gltf_blueprints::GltfBlueprintsSet;

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
pub enum SavingSet {
    Save,
}

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
pub enum LoadingSet {
    Load,
}

// Plugin configuration

#[derive(Clone, Resource)]
pub struct SaveLoadConfig {
    pub(crate) save_path: PathBuf,
    pub(crate) component_filter: SceneFilter,
    pub(crate) resource_filter: SceneFilter,
}

// define the plugin

pub struct SaveLoadPlugin {
    pub component_filter: SceneFilter,
    pub resource_filter: SceneFilter,
    pub save_path: PathBuf,
}

impl Default for SaveLoadPlugin {
    fn default() -> Self {
        Self {
            component_filter: SceneFilter::default(),
            resource_filter: SceneFilter::default(),
            save_path: PathBuf::from("scenes"),
        }
    }
}

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct StaticEntitiesRoot;

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct DynamicEntitiesRoot;

impl Plugin for SaveLoadPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<Dynamic>()
            .register_type::<StaticEntitiesRoot>()
            // TODO: remove these in bevy 0.13, as these are now registered by default
            .register_type::<Camera3dDepthTextureUsage>()
            .register_type::<ScreenSpaceTransmissionQuality>()
            .register_type::<StaticEntitiesStorage>()
            .add_event::<SaveRequest>()
            .add_event::<LoadRequest>()
            .add_event::<LoadingFinished>()
            .add_event::<SavingFinished>()
            .insert_resource(SaveLoadConfig {
                save_path: self.save_path.clone(),

                component_filter: self.component_filter.clone(),
                resource_filter: self.resource_filter.clone(),
            })
            .configure_sets(
                Update,
                (LoadingSet::Load).chain().before(GltfBlueprintsSet::Spawn), //.before(GltfComponentsSet::Injection)
            )
            .add_systems(
                PreUpdate,
                (prepare_save_game, apply_deferred, save_game, cleanup_save)
                    .chain()
                    .run_if(should_save),
            )
            .add_systems(Update, mark_load_requested)
            .add_systems(
                Update,
                (unload_world, apply_deferred, load_game)
                    .chain()
                    .run_if(resource_exists::<LoadRequested>)
                    .run_if(not(resource_exists::<LoadFirstStageDone>))
                    .in_set(LoadingSet::Load),
            )
            .add_systems(
                Update,
                (load_static, apply_deferred, cleanup_loaded_scene)
                    .chain()
                    .run_if(resource_exists::<LoadFirstStageDone>)
                    // .run_if(in_state(AppState::LoadingGame))
                    .in_set(LoadingSet::Load),
            );
    }
}
