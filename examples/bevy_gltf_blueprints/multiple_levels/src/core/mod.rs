pub mod camera;
pub use camera::*;

pub mod lighting;
pub use lighting::*;

pub mod relationships;
pub use relationships::*;

pub mod physics;
pub use physics::*;

// pub mod save_load;
// pub use save_load::*;

use bevy::prelude::*;
use bevy_gltf_blueprints::*;

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((
            LightingPlugin,
            CameraPlugin,
            PhysicsPlugin,
            // SaveLoadPlugin,
            BlueprintsPlugin {
                library: BlueprintsLibrary::Folder("models/library".into()),
                ..Default::default()
            },
        ));
    }
}
