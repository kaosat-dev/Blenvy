use bevy::prelude::*;
use bevy_gltf_worlflow_examples_common::CommonPlugin as CommonBasePlugin;

pub use bevy_gltf_worlflow_examples_common::*;

mod physics;

pub struct CommonPlugin;
impl Plugin for CommonPlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((physics::plugin, CommonBasePlugin));
    }
}
