pub mod camera;
use bevy_rapier3d::prelude::Velocity;
pub use camera::*;

pub mod lighting;
pub use lighting::*;

pub mod relationships;
pub use relationships::*;

pub mod physics;
pub use physics::*;

// pub mod blueprints;
// pub use blueprints::*;

pub mod save_load;
pub use save_load::*;

use bevy::prelude::*;
use bevy_gltf_blueprints::*;

use rand::Rng;

fn spawn_test(
    keycode: Res<Input<KeyCode>>,
    mut commands: Commands,

    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,
) {
    if keycode.just_pressed(KeyCode::T) {
        let world = game_world.single_mut();
        let world = world.1[0];

        let mut rng = rand::thread_rng();
        let range = 5.5;
        let x: f32 = rng.gen_range(-range..range);
        let y: f32 = rng.gen_range(-range..range);

        let mut rng = rand::thread_rng();
        let range = 0.8;
        let vel_x: f32 = rng.gen_range(-range..range);
        let vel_y: f32 = rng.gen_range(2.0..2.5);
        let vel_z: f32 = rng.gen_range(-range..range);

        let name_index: u64 = rng.gen();

        let new_entity = commands
            .spawn((
                BluePrintBundle {
                    blueprint: BlueprintName("Health_Pickup".to_string()),
                    transform: TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                    ..Default::default()
                },
                bevy::prelude::Name::from(format!("test{}", name_index)),
                // BlueprintName("Health_Pickup".to_string()),
                // SpawnHere,
                // TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
                Velocity {
                    linvel: Vec3::new(vel_x, vel_y, vel_z),
                    angvel: Vec3::new(0.0, 0.0, 0.0),
                },
            ))
            .id();
        commands.entity(world).add_child(new_entity);
    }
}

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((
            LightingPlugin,
            CameraPlugin,
            PhysicsPlugin,
            SaveLoadPlugin,
            BlueprintsPlugin {
                library_folder: "animation/models/library".into(),
            },
        ))
        // just for testing
        .add_systems(Update, spawn_test);
    }
}
