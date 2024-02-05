pub mod export_types;
use std::path::PathBuf;

use bevy_app::Startup;
use bevy_ecs::system::Resource;
pub use export_types::*;

use bevy::{
    prelude::{App, Plugin},
    scene::SceneFilter,
};

// Plugin configuration
#[derive(Clone, Resource)]
pub struct ExportComponentsConfig {
    pub(crate) save_path: PathBuf,
    #[allow(dead_code)]
    pub(crate) component_filter: SceneFilter, // unused for now
    #[allow(dead_code)]
    pub(crate) resource_filter: SceneFilter, // unused for now
}

pub struct ExportRegistryPlugin {
    pub component_filter: SceneFilter,
    pub resource_filter: SceneFilter,
    pub save_path: PathBuf,
}

impl Default for ExportRegistryPlugin {
    fn default() -> Self {
        Self {
            component_filter: SceneFilter::default(), // unused for now
            resource_filter: SceneFilter::default(),  // unused for now
            save_path: PathBuf::from("assets/registry.json"),
        }
    }
}

impl Plugin for ExportRegistryPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(ExportComponentsConfig {
            save_path: self.save_path.clone(),
            component_filter: self.component_filter.clone(),
            resource_filter: self.resource_filter.clone(),
        })
        .add_systems(Startup, export_types);
    }
}
