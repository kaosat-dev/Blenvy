pub mod spawn_from_blueprints;
pub use spawn_from_blueprints::*;

pub mod spawn_post_process;
pub(crate) use spawn_post_process::*;

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
    pub spawn_here: SpawnHere,
}
impl Default for BluePrintBundle {
    fn default() -> Self {
        BluePrintBundle {
            blueprint: BlueprintInfo{ name: "default".into(), path:"".into()},
            spawn_here: SpawnHere,
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
            material_library: false
        }
    }
}

fn aabbs_enabled(blenvy_config: Res<BlenvyConfig>) -> bool {
    blenvy_config.aabbs
}


impl Plugin for BlueprintsPlugin {
    fn build(&self, app: &mut App) {
        app
            .register_type::<BlueprintInfo>()
            .register_type::<MaterialInfo>()
            .register_type::<SpawnHere>()
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
            .register_type::<BlenvyAssets>()

            .add_event::<BlueprintEvent>()



            .register_type::<HashMap<String, Vec<String>>>()
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
                    blueprints_spawn,

                    /*(
                        prepare_blueprints,
                        blueprints_check_assets_loading,
                        blueprints_spawn,
                        apply_deferred,
                    )
                        .chain(),*/
                    (compute_scene_aabbs, apply_deferred)
                        .chain()
                        .run_if(aabbs_enabled),
                    apply_deferred,
                    (
                        materials_inject,
                        check_for_material_loaded,
                        materials_inject2,
                    )
                        .chain()
                )
                    .chain()
                    .in_set(GltfBlueprintsSet::Spawn),
            )
            .add_systems(
                Update,
                (spawned_blueprint_post_process, apply_deferred)
                    .chain()
                    .in_set(GltfBlueprintsSet::AfterSpawn),
            )
            /* .add_systems(
                Update,
                (
                    trigger_instance_animation_markers_events,
                    trigger_blueprint_animation_markers_events,
                ),
            )*/
            ;
    }
}
