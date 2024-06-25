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
use bevy_gltf_components::{ComponentsFromGltfPlugin, GltfComponentsSet};

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
/// set for the two stages of blueprint based spawning :
pub enum GltfBlueprintsSet {
    Spawn,
    AfterSpawn,
}

#[derive(Bundle)]
pub struct BluePrintBundle {
    pub blueprint: BlueprintName,
    pub blueprint_path: BlueprintPath,
    pub spawn_here: SpawnHere,
}
impl Default for BluePrintBundle {
    fn default() -> Self {
        BluePrintBundle {
            blueprint: BlueprintName("default".into()),
            blueprint_path: BlueprintPath("".into()),
            spawn_here: SpawnHere,
        }
    }
}

#[derive(Clone, Resource)]
pub struct BluePrintsConfig {
    pub(crate) aabbs: bool,
    pub(crate) aabb_cache: HashMap<String, Aabb>, // cache for aabbs

    pub(crate) material_library: bool,
    pub(crate) material_library_cache: HashMap<String, Handle<StandardMaterial>>,
}

#[derive(Debug, Clone, Copy, Eq, PartialEq, Hash, Default)]
pub enum GltfFormat {
    #[default]
    GLB,
    GLTF,
}

impl fmt::Display for GltfFormat {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            GltfFormat::GLB => {
                write!(f, "glb",)
            }
            GltfFormat::GLTF => {
                write!(f, "gltf")
            }
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

fn aabbs_enabled(blueprints_config: Res<BluePrintsConfig>) -> bool {
    blueprints_config.aabbs
}

fn materials_library_enabled(blueprints_config: Res<BluePrintsConfig>) -> bool {
    blueprints_config.material_library
}

impl Plugin for BlueprintsPlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins(ComponentsFromGltfPlugin {})
            .register_type::<BlueprintName>()
            .register_type::<BlueprintPath>()
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
            .register_type::<LocalAssets>()
            .register_type::<BlueprintAssets>()


            .register_type::<HashMap<String, Vec<String>>>()
            .insert_resource(BluePrintsConfig {

                aabbs: self.aabbs,
                aabb_cache: HashMap::new(),

                material_library: self.material_library,
                material_library_cache: HashMap::new(),
            })
            .configure_sets(
                Update,
                (GltfBlueprintsSet::Spawn, GltfBlueprintsSet::AfterSpawn)
                    .chain()
                    .after(GltfComponentsSet::Injection),
            )
            .add_systems(
                Update,
                (
                    test_thingy,
                    check_for_loaded2,
                    spawn_from_blueprints2,

                    /*(
                        prepare_blueprints,
                        check_for_loaded,
                        spawn_from_blueprints,
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
                        .run_if(materials_library_enabled),
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
