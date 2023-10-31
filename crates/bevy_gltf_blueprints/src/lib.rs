pub mod spawn_from_blueprints;
pub use spawn_from_blueprints::*;

pub mod spawn_post_process;
pub use spawn_post_process::*;

pub mod animation;
pub use animation::*;

pub mod clone_entity;
pub use clone_entity::*;

use std::path::PathBuf;

use bevy::prelude::*;
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
    pub spawn_here: SpawnHere,
    pub transform: TransformBundle,
}
impl Default for BluePrintBundle {
    fn default() -> Self {
        BluePrintBundle {
            blueprint: BlueprintName("default".into()),
            spawn_here: SpawnHere,
            transform: TransformBundle::default(),
        }
    }
}

#[derive(Clone, Resource)]
pub(crate) struct BluePrintsConfig {
    pub(crate) library_folder: PathBuf,
}

#[derive(Debug, Clone)]
pub struct BlueprintsPlugin {
    /// The base folder where library/blueprints assets are loaded from, relative to the executable.
    pub library_folder: PathBuf,
}

impl Default for BlueprintsPlugin {
    fn default() -> Self {
        Self {
            library_folder: PathBuf::from("models/library"),
        }
    }
}

impl Plugin for BlueprintsPlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins(ComponentsFromGltfPlugin)
            .register_type::<BlueprintName>()
            .register_type::<SpawnHere>()
            .register_type::<Animations>()
            .insert_resource(BluePrintsConfig {
                library_folder: self.library_folder.clone(),
            })
            .configure_sets(
                Update,
                (GltfBlueprintsSet::Spawn, GltfBlueprintsSet::AfterSpawn)
                    .chain()
                    .after(GltfComponentsSet::Injection),
            )
            .add_systems(
                Update,
                (spawn_from_blueprints)
                    // .run_if(in_state(AppState::AppRunning).or_else(in_state(AppState::LoadingGame))) // FIXME: how to replace this with a crate compatible version ?
                    .in_set(GltfBlueprintsSet::Spawn),
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
                    // .run_if(in_state(AppState::LoadingGame).or_else(in_state(AppState::AppRunning))) // FIXME: how to replace this with a crate compatible version ?
                    .in_set(GltfBlueprintsSet::AfterSpawn),
            );
    }
}
