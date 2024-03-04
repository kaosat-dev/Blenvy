pub mod camera;
pub use camera::*;

//pub mod relationships;
//pub use relationships::*;

use bevy::prelude::*;

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins(CameraPlugin);
    }
}
