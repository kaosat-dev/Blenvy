use bevy::{gltf::Gltf, prelude::*};
use bevy_editor_pls::prelude::*;
use bevy_gltf_components::ComponentsFromGltfPlugin;
use bevy_rapier3d::prelude::*;

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
            DefaultPlugins.set(AssetPlugin::default()),
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
pub struct MyGltf(pub Handle<Gltf>);

// we preload the data here, but this is for DEMO PURPOSES ONLY !! Please use https://github.com/NiklasEi/bevy_asset_loader or a similar logic to seperate loading / pre processing
// of assets from the spawning
// MyGltf is also just for the same purpose, you do not need it in a real scenario
// the states here are also for demo purposes only,
fn setup(mut commands: Commands, asset_server: Res<AssetServer>) {
    commands.insert_resource(MyGltf(asset_server.load("models/level1.glb")));
}

fn spawn_level(
    mut commands: Commands,
    scene_markers: Query<&LoadedMarker>,
    mut asset_event_reader: EventReader<AssetEvent<Gltf>>,
    mut next_state: ResMut<NextState<AppState>>,
    models: Res<Assets<bevy::gltf::Gltf>>,
) {
    if let Some(asset_event) = asset_event_reader.read().next() {
        match asset_event {
            AssetEvent::Added { id } => {
                info!("GLTF loaded/ added {:?}", asset_event);
                let my_gltf = models.get(*id).unwrap();
                if scene_markers.is_empty() {
                    info!("spawning scene");
                    commands.spawn((
                        SceneBundle {
                            scene: my_gltf.scenes[0].clone(),
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
