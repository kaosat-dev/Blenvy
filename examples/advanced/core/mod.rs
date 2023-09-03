pub mod camera;
pub use camera::*;

pub mod lighting;
pub use lighting::*;

pub mod relationships;
pub use relationships::*;

pub mod physics;
pub use physics::*;

pub mod spawning;
pub use spawning::*;

pub mod save_load;
pub use save_load::*;

use bevy::prelude::*;
pub struct CorePlugin;
impl Plugin for CorePlugin {
  fn build(&self, app: &mut App) {
      app
        .add_plugins((
            LightingPlugin,
            CameraPlugin,
            PhysicsPlugin, 
            SpawningPlugin,
            SaveLoadPlugin
        ));
  }
}
