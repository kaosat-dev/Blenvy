
/*pub mod spawn_entities;
pub use spawn_entities::*;

pub mod spawning_components;
pub use spawning_components::*;

pub mod spawning_events;
pub use spawning_events::*;*/


use bevy::{prelude::*, gltf::Gltf};

use crate::{test_components::BlueprintName, assets::GameAssets, state::AppState};

pub fn spawn_placeholders(
    spawn_placeholders: Query<(Entity, &BlueprintName, &Transform), Added<BlueprintName>>,

    mut commands: Commands,
    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,
    game_assets: Res<GameAssets>,
    assets_gltf: Res<Assets<Gltf>>,

    // mut spawn_requested_events: EventWriter<SpawnRequestedEvent>,
){

    for (entity, blupeprint_name, global_transform) in spawn_placeholders.iter() {
        info!("need to spawn {:?}", blupeprint_name.0);
        let what = &blupeprint_name.0;
        let model_path = format!("models/library/{}.glb", &what);
        let scene = game_assets.models.get(&model_path).expect(&format!("no matching model {:?} found", model_path));
        println!("fooooo {:?}",game_assets.models.keys());
        info!("attempting to spawn {:?}",model_path);

        let world = game_world.single_mut();
        let world = world.1[0]; // FIXME: dangerous hack because our gltf data have a single child like this, but might not always be the case
        
        let gltf = assets_gltf.get(scene).expect("this gltf should have been loaded");
        println!("baaaar {:?}", &gltf.named_scenes);
        let scene = &gltf.named_scenes["library"]; // TODO: carefull ! this needs to match the blender scene name !!! including lower/upper casing


        let position = global_transform.translation;
        println!("POSITION {}", position);
        //spawn_requested_events.send(SpawnRequestedEvent { what: "enemy".into(), position, amount: 1, spawner_id: None });
        let child_scene = commands.spawn(
          (
              SceneBundle {
                  scene: scene.clone(),
                  transform: Transform::from_translation(position),
                  ..Default::default()
              },
              bevy::prelude::Name::from(["scene_wrapper", &what.clone()].join("_") ),
              // Parent(world) // FIXME/ would be good if this worked directly
              /*SpawnedRoot,
              AnimationHelper{ // TODO: insert this at the ENTITY level, not the scene level
                named_animations: gltf.named_animations.clone(),
                // animations: gltf.named_animations.values().clone()
              },*/
          )).id();
          commands.entity(world).add_child(child_scene);
    }
}


// TODO: move this out, likely
// this is a flag component for our levels/game world
#[derive(Component)]
pub struct GameWorldTag;


pub struct SpawningPlugin;
impl Plugin for SpawningPlugin {
  fn build(&self, app: &mut App) {
      app
        .add_systems(Update, spawn_placeholders.run_if(in_state(AppState::GameRunning)))
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