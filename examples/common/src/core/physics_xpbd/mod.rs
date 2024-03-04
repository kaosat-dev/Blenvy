pub(crate) mod physics_replace_proxies;
pub(crate) use physics_replace_proxies::*;

pub(crate) mod utils;

pub(crate) mod controls;
pub(crate) use controls::*;

use bevy::prelude::*;
use bevy_xpbd_3d::prelude::*;

use crate::state::GameState;
use bevy_gltf_blueprints::GltfBlueprintsSet;

pub struct PhysicsPluginXPBD;
impl Plugin for PhysicsPluginXPBD {
    fn build(&self, app: &mut App) {
        app.add_plugins((PhysicsPlugins::default(), PhysicsDebugPlugin::default()))
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
