use bevy::prelude::*;
use bevy::tasks::IoTaskPool;
use std::io::Write;
use std::fs::File;

use crate::game::{Pickable, Player};

use super::Saveable;


const NEW_SCENE_FILE_PATH:&str="save.scn.ron";

pub fn should_save(
    keycode: Res<Input<KeyCode>>,
) -> bool {
    return keycode.just_pressed(KeyCode::S)
}

pub fn save_game(
    world: &mut World,
){
    info!("saving");

    let mut scene_world = World::new();
    let entities: Vec<Entity> = world
    .query_filtered::<Entity, With<Saveable>>()
    .iter(world)
    .collect();

   let mut scene_builder = DynamicSceneBuilder::from_world(world);
    scene_builder
        .allow::<bevy::core::Name>()
        .allow::<Saveable>()
        .allow::<Transform>()
        // .allow::<BlueprintName>()
        .allow::<Pickable>()

        .allow::<Player>()// FIXME: useless ? ...hmm might be needed for dynamically generated entities during the lifetime of the game
        // .allow::<Enemy>()// FIXME: useless ? ...hmm might be needed for dynamically generated entities during the lifetime of the game

        .extract_entities(entities.into_iter());
   let dyn_scene = scene_builder.build();

   let serialized_scene = dyn_scene.serialize_ron(world.resource::<AppTypeRegistry>()).unwrap();


   #[cfg(not(target_arch = "wasm32"))]
          IoTaskPool::get()
              .spawn(async move {
                  // Write the scene RON data to file
                  File::create(format!("assets/{NEW_SCENE_FILE_PATH}"))
                      .and_then(|mut file| file.write(serialized_scene.as_bytes()))
                      .expect("Error while writing scene to file");
              })
              .detach();
}

// let my_uuid = Uuid::new_v4();
fn save_game_alt(
    keycode: Res<Input<KeyCode>>,
    saveables: Query<&Saveable>
){
    if keycode.just_pressed(KeyCode::S) {
        info!("saving");
        println!("saveables {:?}", saveables);

        let serialized_scene ="";
        #[cfg(not(target_arch = "wasm32"))]
        IoTaskPool::get()
            .spawn(async move {
                // Write the scene RON data to file
                File::create(format!("assets/{NEW_SCENE_FILE_PATH}"))
                    .and_then(|mut file| file.write(serialized_scene.as_bytes()))
                    .expect("Error while writing scene to file");
            })
            .detach();
    }
}