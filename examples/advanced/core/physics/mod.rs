pub mod physics_replace_proxies;
pub use physics_replace_proxies::*;

pub mod utils;

pub mod controls;
pub use controls::*;

use crate::state::GameState;
use bevy::prelude::*;
// use super::blueprints::GltfBlueprintsSet;
use bevy_gltf_blueprints::GltfBlueprintsSet;
// use crate::Collider;
pub struct PhysicsPlugin;
impl Plugin for PhysicsPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<AutoAABBCollider>()
            .register_type::<physics_replace_proxies::Collider>()
            // find a way to make serde's stuff serializable
            // .register_type::<bevy_rapier3d::dynamics::CoefficientCombineRule>()
            //bevy_rapier3d::dynamics::CoefficientCombineRule
            .add_systems(
                Update,
                physics_replace_proxies.after(GltfBlueprintsSet::AfterSpawn),
            )
            .add_systems(OnEnter(GameState::InGame), resume_physics)
            .add_systems(OnExit(GameState::InGame), pause_physics);
    }
}
