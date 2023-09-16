pub mod camera;
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
    let name_index:u64 = rng.gen();

    let new_entity = commands.spawn((
      bevy::prelude::Name::from(format!("test{}", name_index)),
      BlueprintName("Health_Pickup".to_string()),
      SpawnHere,
      TransformBundle::from_transform(Transform::from_xyz(x, 1.0, y))
    )).id();
    commands.entity(world).add_child(new_entity);
  }
}

pub struct CorePlugin;
impl Plugin for CorePlugin {
  fn build(&self, app: &mut App) {
      app
        .add_plugins((
            LightingPlugin,
            CameraPlugin,
            PhysicsPlugin, 
            SaveLoadPlugin,
            BlueprintsPlugin
        ))
        
          // just for testing
          .add_systems(
            Update, 
            spawn_test
          )
        ;
  }
}
