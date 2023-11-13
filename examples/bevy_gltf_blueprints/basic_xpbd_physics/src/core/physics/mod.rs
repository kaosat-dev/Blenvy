pub mod physics_replace_proxies;
pub use physics_replace_proxies::*;

pub mod utils;

pub mod controls;
pub use controls::*;

use crate::state::GameState;

use bevy::prelude::*;
use bevy_xpbd_3d::prelude::*;

use bevy_gltf_blueprints::GltfBlueprintsSet;

pub struct PhysicsPlugin;
impl Plugin for PhysicsPlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((PhysicsPlugins::default(), PhysicsDebugPlugin::default()))
            .register_type::<AutoAABBCollider>()
            .register_type::<physics_replace_proxies::Collider>()
            .add_systems(
                Update,
                physics_replace_proxies.after(GltfBlueprintsSet::AfterSpawn),
            )
            .add_systems(OnEnter(GameState::InGame), resume_physics)
            .add_systems(OnExit(GameState::InGame), pause_physics);
    }
}
