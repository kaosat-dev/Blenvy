pub mod physics_replace_proxies;
use bevy_rapier3d::{
    prelude::{NoUserData, RapierPhysicsPlugin},
    render::RapierDebugRenderPlugin,
};
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
        app.add_plugins((
            RapierPhysicsPlugin::<NoUserData>::default(),
            RapierDebugRenderPlugin::default(),
        ))
        .register_type::<AutoAABBCollider>()
        .register_type::<physics_replace_proxies::Collider>()
        .add_systems(
            Update,
            physics_replace_proxies.after(GltfBlueprintsSet::AfterSpawn),
        )
        // physics controls
        .add_systems(OnEnter(GameState::InGame), resume_physics)
        .add_systems(OnExit(GameState::InGame), pause_physics)
        .add_systems(Update, toggle_physics_debug)
        ;
    }
}
