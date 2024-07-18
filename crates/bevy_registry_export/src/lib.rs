pub mod export_types;
use std::path::PathBuf;

use bevy_app::Startup;
use bevy_ecs::system::Resource;
pub use export_types::*;

use bevy::{
    asset::AssetPlugin,
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
            component_filter: SceneFilter::default(),  // unused for now
            resource_filter: SceneFilter::default(),   // unused for now
            save_path: PathBuf::from("registry.json"), // relative to assets folder
        }
    }
}

impl Plugin for ExportRegistryPlugin {
    fn build(&self, app: &mut App) {
        app.register_asset_root()
            .insert_resource(ExportComponentsConfig {
                save_path: self.save_path.clone(),
                component_filter: self.component_filter.clone(),
                resource_filter: self.resource_filter.clone(),
            })
            .add_systems(Startup, export_types);
    }
}

trait RegistryExportApp {
    fn register_asset_root(&mut self) -> &mut Self;
}
impl RegistryExportApp for App {
    fn register_asset_root(&mut self) -> &mut Self {
        let asset_plugin = get_asset_plugin(self);
        let path_str = asset_plugin.file_path.clone();
        let path = PathBuf::from(path_str);
        self.insert_resource(AssetRoot(path))
    }
}

fn get_asset_plugin(app: &App) -> &AssetPlugin {
    let asset_plugins: Vec<&AssetPlugin> = app.get_added_plugins();
    asset_plugins.into_iter().next().expect(ASSET_ERROR)
}

const ASSET_ERROR: &str = "Bevy_registry_export requires access to the Bevy asset plugin. \
    Please add `ExportRegistryPlugin` after `AssetPlugin`, which is commonly added as part of the `DefaultPlugins`";

#[derive(Debug, Clone, PartialEq, Eq, Hash, Resource)]
pub(crate) struct AssetRoot(pub(crate) PathBuf);
