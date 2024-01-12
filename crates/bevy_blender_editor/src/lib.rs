pub mod export_types;
use std::{fs::File, path::PathBuf};

use bevy_app::Startup;
use bevy_ecs::system::Resource;
pub use export_types::*;

use bevy::{prelude::{App, IntoSystemConfigs, Plugin, SystemSet, Update}, scene::SceneFilter};


// Plugin configuration

#[derive(Clone, Resource)]
pub struct ExportComponentsConfig {
    pub(crate) save_path: PathBuf,
    pub(crate) component_filter: SceneFilter,
    pub(crate) resource_filter: SceneFilter,
}

pub struct ExportComponentsPlugin{
    pub component_filter: SceneFilter,
    pub resource_filter: SceneFilter,
    pub save_path: PathBuf,
}

impl Default for ExportComponentsPlugin {
    fn default() -> Self {
        Self {
            component_filter: SceneFilter::default(),
            resource_filter: SceneFilter::default(),
            save_path: PathBuf::from("."),
        }
    }
}

impl Plugin for ExportComponentsPlugin {

    fn build(&self, app: &mut App) {

        let mut file = File::create("schema.json").expect("should have created schema file");
        // file.write_all(b"Hello, world!")?;
        app
            .insert_resource(ExportComponentsConfig {
                save_path: self.save_path.clone(),
                component_filter: self.component_filter.clone(),
                resource_filter: self.resource_filter.clone(),
            })
            .add_systems(Startup, export_types)
            // .export_types(file)//std::io::stdout())
          ;
    }
}
