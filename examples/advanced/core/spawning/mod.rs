use bevy::prelude::*;

use crate::test_components::BlueprintName;

pub fn spawn_placeholders(
    spawn_placeholders: Query<(Entity, &BlueprintName), Added<BlueprintName>>,
){

    for (entity, blupeprint_name) in spawn_placeholders.iter() {
        info!("need to spawn {:?}", blupeprint_name.0)
    }
}
pub struct SpawningPlugin;
impl Plugin for SpawningPlugin {
  fn build(&self, app: &mut App) {
      app
        .add_systems(Update, spawn_placeholders)
        /* .register_type::<Spawner>()
        .add_event::<SpawnRequestedEvent>()
        .add_event::<DespawnRequestedEvent>()
    
        .add_systems(
          Update,
          (
            // spawn_entities, 
            spawn_entities2,
            update_spawned_root_first_child, 
            cleanup_scene_instances,
          ).run_if(in_state(GameState::InGame))
        )
        .add_systems(
          PostUpdate, 
          despawn_entity.after(bevy::render::view::VisibilitySystems::CalculateBounds) // found this after digging around in Bevy discord, not 100M sure of its reliability
        )*/
      ;
  }
}