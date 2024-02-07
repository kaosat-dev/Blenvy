use bevy::prelude::*;
use bevy_gltf_blueprints::*;

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((BlueprintsPlugin {
            library_folder: "models/library".into(),
            material_library: true,
            ..Default::default()
        },));
    }
}
