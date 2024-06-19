use std::path::PathBuf;
use bevy::{prelude::*, render::primitives::Aabb, utils::HashMap};

pub mod components;
pub use components::*;

pub mod registry;
pub use registry::*;

pub mod blueprints;
pub use blueprints::*;

#[derive(Clone, Resource)]
pub struct BlenvyConfig {
    // registry
    pub(crate) registry_save_path: PathBuf,
    pub(crate) registry_component_filter: SceneFilter,
    #[allow(dead_code)]
    pub(crate) registry_resource_filter: SceneFilter,

    // blueprints
    pub(crate) aabbs: bool,
    pub(crate) aabb_cache: HashMap<String, Aabb>, // cache for aabbs
    pub(crate) materials_cache: HashMap<String, Handle<StandardMaterial>>, // cache for materials
}


#[derive(Debug, Clone)]
/// Plugin for gltf blueprints
pub struct BlenvyPlugin {
    pub registry_save_path: PathBuf,

    pub registry_component_filter: SceneFilter,
    pub registry_resource_filter: SceneFilter,

    /// Automatically generate aabbs for the blueprints root objects
    pub aabbs: bool,
}

impl Default for BlenvyPlugin {
    fn default() -> Self {
        Self {
            registry_save_path: PathBuf::from("registry.json"), // relative to assets folder
            registry_component_filter: SceneFilter::default(),
            registry_resource_filter: SceneFilter::default(),
            aabbs: false,
        }
    }
}

impl Plugin for BlenvyPlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((
            ComponentsFromGltfPlugin::default(), 
            ExportRegistryPlugin::default(),
            BlueprintsPlugin::default()
        ))
        .insert_resource(BlenvyConfig {
            registry_save_path: self.registry_save_path.clone(),
            registry_component_filter: self.registry_component_filter.clone(),
            registry_resource_filter: self.registry_resource_filter.clone(),

            aabbs: self.aabbs,
            aabb_cache: HashMap::new(),

            materials_cache: HashMap::new(),
        })
        ;

    }
}