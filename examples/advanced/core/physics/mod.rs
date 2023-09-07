pub mod physics_replace_proxies;
pub use physics_replace_proxies::*;

pub mod utils;

pub mod controls;
pub use controls::*;

use bevy::prelude::*;
use crate::state::GameState;
use super::spawning::SpawnSet;

// use crate::Collider;
pub struct PhysicsPlugin;
impl Plugin for PhysicsPlugin {
  fn build(&self, app: &mut App) {
      app
        .register_type::<AutoAABBCollider>()
        .register_type::<physics_replace_proxies::Collider>()
        .register_type::<physics_replace_proxies::RigidBodyProxy>()

        // find a way to make serde's stuff serializable
        // .register_type::<bevy_rapier3d::dynamics::CoefficientCombineRule>()
        //bevy_rapier3d::dynamics::CoefficientCombineRule

        .add_systems(Update, physics_replace_proxies.after(SpawnSet::AfterSpawn))

        .add_systems(
          OnEnter(GameState::InGame),
          resume_physics
        )
        .add_systems(
          OnExit(GameState::InGame),
          pause_physics
        )
      ;
  }
}

