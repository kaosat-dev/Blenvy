use std::time::Duration;
use bevy::{prelude::*, asset::ChangeWatcher, gltf::Gltf};
use bevy_editor_pls::prelude::*;
use bevy_rapier3d::prelude::*;
use bevy_gltf_components::ComponentsFromGltfPlugin;

mod core;
use crate::core::*;

pub mod assets;
use assets::*;

pub mod state;
use state::*;

mod game;
use game::*;

mod test_components;
use test_components::*;



fn main(){
    App::new()
    .add_plugins((
        DefaultPlugins.set(
            AssetPlugin {
                // This tells the AssetServer to watch for changes to assets.
                // It enables our scenes to automatically reload in game when we modify their files.
                // practical in our case to be able to edit the shaders without needing to recompile
                watch_for_changes: ChangeWatcher::with_delay(Duration::from_millis(50)),
                ..default()
            }
        ),
        // editor
        EditorPlugin::default(),
        // physics
        RapierPhysicsPlugin::<NoUserData>::default(),
        RapierDebugRenderPlugin::default(),
        // our custom plugins
        ComponentsFromGltfPlugin,

        StatePlugin,
        AssetsPlugin,
        CorePlugin, // reusable plugins
        GamePlugin, // specific to our game
        ComponentsTestPlugin // Showcases different type of components /structs
    ))
    .run();
}
