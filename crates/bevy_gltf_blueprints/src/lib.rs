
pub mod spawn_from_blueprints;
use bevy_gltf_components::GltfComponentsSet;
pub use spawn_from_blueprints::*;

pub mod spawn_post_process;
pub use spawn_post_process::*;

pub mod clone_entity;
pub use clone_entity::*;

use bevy::prelude::*;

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
pub enum GltfBlueprintsSet{
  Spawn,
  AfterSpawn, 
}


pub struct BlueprintsPlugin;
impl Plugin for BlueprintsPlugin {
  fn build(&self, app: &mut App) {
      app
        .register_type::<BlueprintName>()
        .register_type::<SpawnHere>()
        /* .register_type::<Spawner>()
        .add_event::<SpawnRequestedEvent>()
        .add_event::<DespawnRequestedEvent>()*/
        .configure_sets(
          Update,
          (GltfBlueprintsSet::Spawn, GltfBlueprintsSet::AfterSpawn).chain().after(GltfComponentsSet::Injection)
        )

        .add_systems(Update, 
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
        )


        /* .add_systems(
          PostUpdate, 
          despawn_entity.after(bevy::render::view::VisibilitySystems::CalculateBounds) // found this after digging around in Bevy discord, not 100M sure of its reliability
        )*/
      ;
  }
}