
pub mod spawn_entities;
pub use spawn_entities::*;

pub mod clone_entity;
pub use clone_entity::*;

/*pub mod spawning_components;
pub use spawning_components::*;

pub mod spawning_events;
pub use spawning_events::*;*/


use bevy::{prelude::*, gltf::Gltf};

use crate::{test_components::BlueprintName, assets::GameAssets, state::{AppState, GameState}};

#[derive(Component, Reflect, Default, Debug, )]
#[reflect(Component)]
pub struct SpawnHere;

#[derive(Component)]
pub struct Original(Entity);

// also takes into account the already exisiting override components ?? ie any component overrides
pub fn spawn_placeholders(
    spawn_placeholders: Query<(Entity, &Name, &BlueprintName, &Transform), (Added<BlueprintName>, Added<SpawnHere>, Without<Spawned>, Without<SpawnedRoot>)>,

    mut commands: Commands,
    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,
    game_assets: Res<GameAssets>,
    assets_gltf: Res<Assets<Gltf>>,

    // mut spawn_requested_events: EventWriter<SpawnRequestedEvent>,
){

    for (entity, name, blupeprint_name, global_transform) in spawn_placeholders.iter() {
        info!("need to spawn {:?}", blupeprint_name.0);
        let what = &blupeprint_name.0;
        let model_path = format!("models/library/{}.glb", &what);
        let scene = game_assets.models.get(&model_path).expect(&format!("no matching model {:?} found", model_path));
        info!("attempting to spawn {:?}",model_path);

        let world = game_world.single_mut();
        let world = world.1[0]; // FIXME: dangerous hack because our gltf data have a single child like this, but might not always be the case
        
        let gltf = assets_gltf.get(scene).expect("this gltf should have been loaded");
        // WARNING we work under the assumtion that there is ONLY ONE named scene, and that the first one is the right one
        let main_scene_name =gltf.named_scenes.keys().nth(0).expect("there should be at least one named scene in the gltf file to spawn");
        let scene = &gltf.named_scenes[main_scene_name];


        //spawn_requested_events.send(SpawnRequestedEvent { what: "enemy".into(), position, amount: 1, spawner_id: None });
        let child_scene = commands.spawn(
          (
              SceneBundle {
                  scene: scene.clone(),
                  transform: global_transform.clone(),
                  ..Default::default()
              },
              bevy::prelude::Name::from(["scene_wrapper", &name.clone()].join("_") ),
              // Parent(world) // FIXME/ would be good if this worked directly
              SpawnedRoot,
              /*AnimationHelper{ // TODO: insert this at the ENTITY level, not the scene level
                named_animations: gltf.named_animations.clone(),
                // animations: gltf.named_animations.values().clone()
              },*/
              Original(entity)
          )).id();
          commands.entity(world).add_child(child_scene);
    }
}

use rand::Rng;

fn spawn_test(
  keycode: Res<Input<KeyCode>>,
  mut commands: Commands,

  mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,
  

) {
  if keycode.just_pressed(KeyCode::T) {
    let world = game_world.single_mut();
    let world = world.1[0];

    let mut rng = rand::thread_rng();
    let range = 5.5;
    let x: f32 = rng.gen_range(-range..range);
    let y: f32 = rng.gen_range(-range..range);
    let name_index:u64 = rng.gen();

    let new_entity = commands.spawn((
      bevy::prelude::Name::from(format!("test{}", name_index)),
      BlueprintName("Health_Pickup".to_string()),
      SpawnHere,
      TransformBundle::from_transform(Transform::from_xyz(x, 1.0, y))
    )).id();
    commands.entity(world).add_child(new_entity);
  }
}

#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
pub enum SpawnSet{
  Spawn,
  AfterSpawn, 
}

pub struct SpawningPlugin;
impl Plugin for SpawningPlugin {
  fn build(&self, app: &mut App) {
      app
        .register_type::<SpawnHere>()
        /* .register_type::<Spawner>()
        .add_event::<SpawnRequestedEvent>()
        .add_event::<DespawnRequestedEvent>()*/
        .configure_sets(
          Update,
          (SpawnSet::Spawn, SpawnSet::AfterSpawn).chain()
        )

        // just for testing
        .add_systems(
          Update, 
          spawn_test
        )
    
        .add_systems(Update, 
          (spawn_placeholders).chain()
          .run_if(in_state(AppState::AppRunning).or_else(in_state(AppState::LoadingGame)))
          .in_set(SpawnSet::Spawn),
        )

         .add_systems(
          Update,
          (
            // spawn_entities,
            update_spawned_root_first_child, 
            cleanup_scene_instances,
          )
          .chain()
          .run_if(in_state(AppState::LoadingGame).or_else(in_state(AppState::AppRunning)))
          .in_set(SpawnSet::AfterSpawn),
        )


        /* .add_systems(
          PostUpdate, 
          despawn_entity.after(bevy::render::view::VisibilitySystems::CalculateBounds) // found this after digging around in Bevy discord, not 100M sure of its reliability
        )*/
      ;
  }
}