use bevy::{asset::ChangeWatcher, gltf::Gltf, prelude::*};
use bevy_editor_pls::prelude::*;
use bevy_gltf_components::ComponentsFromGltfPlugin;
use bevy_rapier3d::prelude::*;
use std::time::Duration;

mod core;
use crate::core::*;

mod game;
use game::*;

mod test_components;
use test_components::*;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// helper marker component
pub struct LoadedMarker;

#[derive(Debug, Clone, Copy, Default, Eq, PartialEq, Hash, States)]
enum AppState {
    #[default]
    Loading,
    Running,
}

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins.set(AssetPlugin {
                // This tells the AssetServer to watch for changes to assets.
                // It enables our scenes to automatically reload in game when we modify their files.
                // practical in our case to be able to edit the shaders without needing to recompile
                watch_for_changes: ChangeWatcher::with_delay(Duration::from_millis(50)),
                ..default()
            }),
            // editor
            EditorPlugin::default(),
            // physics
            RapierPhysicsPlugin::<NoUserData>::default(),
            RapierDebugRenderPlugin::default(),
            // our custom plugins
            ComponentsFromGltfPlugin,
            CorePlugin,           // reusable plugins
            DemoPlugin,           // specific to our game
            ComponentsTestPlugin, // Showcases different type of components /structs
        ))
        .add_state::<AppState>()
        .add_systems(Startup, setup)
        .add_systems(Update, (spawn_level.run_if(in_state(AppState::Loading)),))
        .run();
}

#[derive(Resource)]
struct AssetLoadHelper(Handle<Scene>);
// we preload the data here, but this is for DEMO PURPOSES ONLY !! Please use https://github.com/NiklasEi/bevy_asset_loader or a similar logic to seperate loading / pre processing
// of assets from the spawning
// AssetLoadHelper is also just for the same purpose, you do not need it in a real scenario
// the states here are also for demo purposes only,
fn setup(mut commands: Commands, asset_server: Res<AssetServer>) {
    let tmp: Handle<Scene> = asset_server.load("basic/models/level1.glb#Scene0");
    commands.insert_resource(AssetLoadHelper(tmp));
}

fn spawn_level(
    mut commands: Commands,
    scene_markers: Query<&LoadedMarker>,
    preloaded_scene: Res<AssetLoadHelper>,

    mut asset_event_reader: EventReader<AssetEvent<Gltf>>,
    mut next_state: ResMut<NextState<AppState>>,
) {
    if let Some(asset_event) = asset_event_reader.iter().next() {
        match asset_event {
            AssetEvent::Created { handle: _ } => {
                info!("GLTF loaded");
                if scene_markers.is_empty() {
                    info!("spawning scene");
                    commands.spawn((
                        SceneBundle {
                            scene: preloaded_scene.0.clone(),
                            ..default()
                        },
                        LoadedMarker,
                        Name::new("Level1"),
                    ));
                    next_state.set(AppState::Running);
                }
            }
            _ => (),
        }
    }
}
