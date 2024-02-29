use bevy::prelude::*;
use bevy_gltf_blueprints::*;
use bevy_registry_export::*;

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((
            ExportRegistryPlugin {
                save_path: "registry.json".into(),
                ..Default::default()
            },
            BlueprintsPlugin {
                legacy_mode: false,
                library_folder: "models/library".into(),
                format: GltfFormat::GLB,
                aabbs: true,
                ..Default::default()
            },
        ));
    }
}
