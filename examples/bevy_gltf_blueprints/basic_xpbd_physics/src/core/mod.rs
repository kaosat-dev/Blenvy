pub mod physics;
pub use physics::*;

use bevy::prelude::*;
use bevy_gltf_blueprints::*;

use bevy_xpbd_3d::plugins::PhysicsDebugPlugin;

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((
            PhysicsPlugin,
            //PhysicsDebugPlugin::default(),
            BlueprintsPlugin {
                library_folder: "models/library".into(),
                ..Default::default()
            },
        ));
    }
}
