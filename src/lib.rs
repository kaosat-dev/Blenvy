pub mod utils;
pub use utils::*;

pub mod gltf_to_components;
pub use gltf_to_components::*;

pub mod process_gltfs;
pub use process_gltfs::*;

use bevy::prelude::{
  App,Plugin, PreUpdate
};

#[derive(Default)]
pub struct ProcessGltfPlugin;
impl Plugin for ProcessGltfPlugin {
  fn build(&self, app: &mut App) {
      app
        .insert_resource(GltfLoadingTracker::new())

        .add_systems(PreUpdate, (
          track_new_gltf, 
          process_loaded_scenes,
        ))
      ;
  }
}
