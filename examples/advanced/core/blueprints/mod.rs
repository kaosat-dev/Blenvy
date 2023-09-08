
pub mod spawn_from_blueprints;
pub use spawn_from_blueprints::*;

pub mod spawn_post_process;
pub use spawn_post_process::*;

pub mod clone_entity;
pub use clone_entity::*;

/*pub mod spawning_components;
pub use spawning_components::*;

pub mod spawning_events;
pub use spawning_events::*;*/


use bevy::prelude::*;
use crate::state::{AppState, GameState};

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

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
pub enum SpawnSet{
  Spawn,
  AfterSpawn, 
}

pub struct SpawningPlugin;
impl Plugin for SpawningPlugin {
  fn build(&self, app: &mut App) {
      app
        .register_type::<BlueprintName>()
        .register_type::<SpawnHere>()
        /* .register_type::<Spawner>()
        .add_event::<SpawnRequestedEvent>()
        .add_event::<DespawnRequestedEvent>()*/
        .configure_sets(
          Update,
          (SpawnSet::Spawn, SpawnSet::AfterSpawn).chain()
        )

        // just for testing
        .add_systems(
          Update, 
          spawn_test
        )
    
        .add_systems(Update, 
          (spawn_from_blueprints).chain()
          .run_if(in_state(AppState::AppRunning).or_else(in_state(AppState::LoadingGame)))
          .in_set(SpawnSet::Spawn),
        )

         .add_systems(
          Update,
          (
            // spawn_entities,
            update_spawned_root_first_child, 
            apply_deferred,
            cleanup_scene_instances,
            apply_deferred,
          )
          .chain()
          .run_if(in_state(AppState::LoadingGame).or_else(in_state(AppState::AppRunning)))
          .in_set(SpawnSet::AfterSpawn),
        )


        /* .add_systems(
          PostUpdate, 
          despawn_entity.after(bevy::render::view::VisibilitySystems::CalculateBounds) // found this after digging around in Bevy discord, not 100M sure of its reliability
        )*/
      ;
  }
}