use bevy::prelude::*;
use bevy_gltf_blueprints::*;
use bevy_registry_export::*;

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((
            ExportRegistryPlugin::default(),
            BlueprintsPlugin {
                library_folder: "blueprints".into(),
                format: GltfFormat::GLB,
                material_library: true,
                aabbs: true,
                ..Default::default()
            },
        ));
    }
}
