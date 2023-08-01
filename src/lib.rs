pub mod utils;
pub use utils::*;

pub mod gltf_to_components;
pub use gltf_to_components::*;

pub mod process_gltfs;
pub use process_gltfs::*;

use bevy::prelude::{
  App,Plugin, PreUpdate
};


/// A Bevy plugin for extracting components from gltf files and automatically adding them to the relevant entities
/// It will automatically run every time you load a gltf file
/// Add this plugin to your Bevy app to get access to this feature
/// ```
/// # use bevy::prelude::*;
/// # use bevy_gltf_components::prelude::*;
/// 
/// 
/// fn main() {
///    App::new()
///         .add_plugins(DefaultPlugins)
///         .add_plugin(GltfComponentsPlugin)
///         .add_startup_system(setup)
///         .add_system(spawn_level)
///         .run();
/// }
/// 
/// fn setup(
/// mut state: ResMut<State>, 
/// asset_server: Res<AssetServer>, 
///  mut commands: bevy::prelude::Commands
/// ){
///  asset_server.load("models/level1.glb#Scene0")
/// }
/// 
/// fn spawn_level(){
/// 
///}
/// ```
#[derive(Default)]
pub struct ComponentsFromGltfPlugin;
impl Plugin for ComponentsFromGltfPlugin {
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
