use std::time::Duration;
use bevy::{prelude::*, asset::ChangeWatcher, gltf::Gltf};
use bevy_editor_pls::prelude::*;
use bevy_rapier3d::prelude::*;

mod process_gltf;
use process_gltf::*;

mod camera;
use camera::*;

mod lighting;
use lighting::*;

mod relationships;
use relationships::*;

mod physics;
use physics::*;


#[derive(Component, Reflect, Default, Debug, )]
#[reflect(Component)]
/// Demo marker component
pub struct Player;

#[derive(Component, Reflect, Default, Debug, )]
#[reflect(Component)]
/// Demo component showing auto injection of components 
pub struct ShouldBeWithPlayer;



#[derive(Component, Reflect, Default, Debug, )]
#[reflect(Component)]
/// Demo marker component
pub struct LoadedMarker;


#[derive(Component, Reflect, Default, Debug, )]
#[reflect(Component)]
/// Demo marker component
pub struct Interactible;

#[derive(Component, Reflect, Default, Debug, )]
#[reflect(Component)]
/// Demo marker component
pub struct MeshCollider;


#[derive(Debug, Clone, Copy, Default, Eq, PartialEq, Hash, States)]
enum AppState {
    #[default]
    Loading,
    Running,
}



use bevy::{prelude::*};


#[derive(Component, Reflect, Default, Debug, )]
#[reflect(Component)]
pub enum SoundMaterial{
  Metal,
  Wood,
  Rock,
  Cloth,
  Squishy, 
  #[default]
  None
}


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
        ProcessGltfPlugin,
        LightingPlugin,
        CameraPlugin,
        PhysicsPlugin
    ))

    .register_type::<Interactible>()
    .register_type::<MeshCollider>()
    .register_type::<SoundMaterial>()


    .register_type::<Player>()
    // little helper utility, to automatically inject components that are dependant on an other component
    // ie, here an Entity with a Player component should also always have a ShouldBeWithPlayer component
    // you get a warning if you use this, as I consider this to be stop-gap solution (usually you should have either a bundle, or directly define all needed components)
    .add_systems(Update, insert_dependant_component::<Player, ShouldBeWithPlayer>)


    .add_state::<AppState>()
    .add_systems(Startup, setup)
    .add_systems(Update, (
        spawn_level.run_if(in_state(AppState::Loading)),
        player_move_demo.run_if(in_state(AppState::Running)),
        test_collision_events
    ))
    .run();
}



#[derive(Resource)]
struct AssetLoadHack(Handle<Scene>);
// we preload the data here, but this is for DEMO PURPOSES ONLY !! Please use https://github.com/NiklasEi/bevy_asset_loader or a similar logic to seperate loading / pre processing 
// of assets from the spawning
// AssetLoadHack is also just for the same purpose, you do not need it in a real scenario
// the states here are also for demo purposes only, 
fn setup(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
) {

    let tmp: Handle<Scene>  = asset_server.load("models/level1.glb#Scene0");
    commands.insert_resource(AssetLoadHack(tmp));
}

fn spawn_level(
    mut commands: Commands,
    scene_markers: Query<&LoadedMarker>,
    preloaded_scene: Res<AssetLoadHack>,

    mut asset_event_reader: EventReader<AssetEvent<Gltf>>,
    mut next_state: ResMut<NextState<AppState>>,
){

    if let Some(asset_event) = asset_event_reader.iter().next() {
        match asset_event {
            AssetEvent::Created { handle: _ } => {
                info!("GLTF loaded");
                if scene_markers.is_empty() {
                    info!("spawning scene");
                    commands.spawn(
                        (
                            SceneBundle {
                                scene: preloaded_scene.0.clone(),
                                ..default()
                            },
                            LoadedMarker,
                            Name::new("Level1")
                        )
                    );
                    next_state.set(AppState::Running);
                }
            }
            _ => ()
        }
    }

   
   
}


fn player_move_demo(
    keycode: Res<Input<KeyCode>>,
    mut players: Query<&mut Transform, With<Player>>,
){

    let speed = 0.2;
    if let Ok(mut player) = players.get_single_mut() {
        if keycode.pressed(KeyCode::Left) {
            player.translation.x += speed;
        }
        if keycode.pressed(KeyCode::Right) {
            player.translation.x -= speed;
        }

        if keycode.pressed(KeyCode::Up) {
            player.translation.z += speed;
        }
        if keycode.pressed(KeyCode::Down) {
            player.translation.z -= speed;
        }
    }
}


// collision tests
pub fn test_collision_events(
    mut collision_events: EventReader<CollisionEvent>,
    mut contact_force_events: EventReader<ContactForceEvent>,
)
{

    for collision_event in collision_events.iter() {
        println!("collision");
        match collision_event {
            CollisionEvent::Started(entity1, entity2 ,_) => {
                println!("collision started")
            }
            CollisionEvent::Stopped(entity1, entity2 ,_) => {
                println!("collision ended")

            }
        }
    }

    for contact_force_event in contact_force_events.iter() {
        println!("Received contact force event: {:?}", contact_force_event);
    }
}