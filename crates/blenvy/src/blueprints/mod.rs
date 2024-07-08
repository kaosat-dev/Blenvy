pub mod spawn_from_blueprints;
pub use spawn_from_blueprints::*;

pub mod animation;
pub use animation::*;

pub mod aabb;
pub use aabb::*;

pub mod assets;
pub use assets::*;

pub mod materials;
pub use materials::*;

pub mod copy_components;
pub use copy_components::*;

pub mod hot_reload;
pub use hot_reload::*;

use core::fmt;
use std::path::PathBuf;

use bevy::{prelude::*, render::primitives::Aabb, utils::HashMap};

use crate::{BlenvyConfig, GltfComponentsSet};

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
/// set for the two stages of blueprint based spawning :
pub enum GltfBlueprintsSet {
    Spawn,
    AfterSpawn,
}

#[derive(Bundle)]
pub struct BluePrintBundle {
    pub blueprint: BlueprintInfo,
    pub spawn_here: SpawnBlueprint,
}
impl Default for BluePrintBundle {
    fn default() -> Self {
        BluePrintBundle {
            blueprint: BlueprintInfo {
                name: "default".into(),
                path: "".into(),
            },
            spawn_here: SpawnBlueprint,
        }
    }
}

#[derive(Debug, Clone)]
/// Plugin for gltf blueprints
pub struct BlueprintsPlugin {
    /// Automatically generate aabbs for the blueprints root objects
    pub aabbs: bool,
    ///
    pub material_library: bool,
}

impl Default for BlueprintsPlugin {
    fn default() -> Self {
        Self {
            aabbs: false,
            material_library: false,
        }
    }
}

fn aabbs_enabled(blenvy_config: Res<BlenvyConfig>) -> bool {
    blenvy_config.aabbs
}

fn hot_reload(watching_for_changes: Res<WatchingForChanges>) -> bool {
    watching_for_changes.0
}

trait BlenvyApp {
    fn register_watching_for_changes(&mut self) -> &mut Self;
}

impl BlenvyApp for App {
    fn register_watching_for_changes(&mut self) -> &mut Self {
        let asset_server = self
            .world()
            .get_resource::<AssetServer>()
            .expect(ASSET_ERROR);

        let watching_for_changes = asset_server.watching_for_changes();
        self.insert_resource(WatchingForChanges(watching_for_changes))
    }
}

#[derive(Debug, Clone, Resource, Default)]
pub(crate) struct WatchingForChanges(pub(crate) bool);
const ASSET_ERROR: &str = ""; // TODO

impl Plugin for BlueprintsPlugin {
    fn build(&self, app: &mut App) {
        app.register_watching_for_changes()
            .add_event::<BlueprintEvent>()
            .register_type::<BlueprintInfo>()
            .register_type::<MaterialInfo>()
            .register_type::<SpawnBlueprint>()
            .register_type::<BlueprintAnimations>()
            .register_type::<SceneAnimations>()
            .register_type::<AnimationInfo>()
            .register_type::<AnimationInfos>()
            .register_type::<Vec<AnimationInfo>>()
            .register_type::<AnimationMarkers>()
            .register_type::<HashMap<u32, Vec<String>>>()
            .register_type::<HashMap<String, HashMap<u32, Vec<String>>>>()
            .add_event::<AnimationMarkerReached>()
            .register_type::<MyAsset>()
            .register_type::<Vec<MyAsset>>()
            .register_type::<Vec<String>>()
            .register_type::<BlueprintAssets>()
            .register_type::<HashMap<String, Vec<String>>>()
            .register_type::<HideUntilReady>()
            .configure_sets(
                Update,
                (GltfBlueprintsSet::Spawn, GltfBlueprintsSet::AfterSpawn)
                    .chain()
                    .after(GltfComponentsSet::Injection),
            )
            .add_systems(
                Update,
                (
                    blueprints_prepare_spawn,
                    blueprints_check_assets_loading,
                    blueprints_assets_ready,
                    blueprints_scenes_spawned,
                    blueprints_cleanup_spawned_scene,
                    // post process
                    inject_materials,
                    compute_scene_aabbs, // .run_if(aabbs_enabled),
                    blueprints_finalize_instances,
                )
                    .chain()
                    .in_set(GltfBlueprintsSet::Spawn),
            )
            /* .add_systems(
                Update,
                (
                    trigger_instance_animation_markers_events,
                    trigger_blueprint_animation_markers_events,
                ),
            )*/
            // hot reload
            .add_systems(Update, react_to_asset_changes.run_if(hot_reload));
    }
}
