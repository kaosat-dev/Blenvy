use bevy::prelude::*;
use bevy_gltf_worlflow_examples_common_rapier::CommonPlugin;

mod core;
use crate::core::*;

mod game;
use game::*;

mod dupe_components;
mod test_components;
use test_components::*;

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins.set(AssetPlugin::default()),
            // our custom plugins
            CommonPlugin,
            CorePlugin,           // reusable plugins
            GamePlugin,           // specific to our game
            ComponentsTestPlugin, // Showcases different type of components /structs
        ))
        .run();
}
