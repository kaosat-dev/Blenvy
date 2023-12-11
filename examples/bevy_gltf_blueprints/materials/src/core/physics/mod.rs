pub mod physics_replace_proxies;
pub use physics_replace_proxies::*;

pub mod utils;

pub mod controls;
pub use controls::*;

use bevy_rapier3d::{
    prelude::{NoUserData, RapierPhysicsPlugin},
    render::RapierDebugRenderPlugin,
};
use bevy::prelude::*;
use bevy_gltf_blueprints::GltfBlueprintsSet;
use crate::state::GameState;

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
        .add_systems(Update, toggle_physics_debug)
        .add_systems(OnEnter(GameState::InGame), resume_physics)
        .add_systems(OnExit(GameState::InGame), pause_physics);
    }
}
