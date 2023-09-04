
const NEW_SCENE_FILE_PATH:&str="save.scn.ron";


#[derive(Component, Reflect, Debug, )]
#[reflect(Component)]
pub struct Saveable{
    id: Uuid
}

impl Default for Saveable{
    fn default() -> Self {
        Saveable{
            id: Uuid::new_v4()
        }
    }
}

#[derive(Component, Reflect, Debug, Default )]
#[reflect(Component)]
pub struct Hackish;


fn save_game2(
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
fn save_game(
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

/// unload the level recursively
fn unload_world(world: &mut World) {
    let entities: Vec<Entity> = world
        // .query_filtered::<Entity, Or<(With<Save>, With<Unload>)>>()
        .query_filtered::<Entity, With<GameWorldTag>>()// our level/world contains this component
        .iter(world)
        .collect();
    for entity in entities {
        // Check the entity again in case it was despawned recursively
        if world.get_entity(entity).is_some() {
            world.entity_mut(entity).despawn_recursive();
        }
    }
}

/// unload saveables
fn unload_saveables(world: &mut World) {
    let entities: Vec<Entity> = world
        .query_filtered::<Entity, With<Saveable>>()// our level/world contains this component
        .iter(world)
        .collect();
    for entity in entities {
        // Check the entity again in case it was despawned recursively
        if world.get_entity(entity).is_some() {
            info!("despawning");
            world.entity_mut(entity).despawn_recursive();
        }
    }
}

use bevy::ecs::component::Components;
use bevy::ecs::entity::EntityMap;
use serde::{Deserialize, Serialize};

// almost identical to setup_game, !!??
fn load_world(
    mut commands: Commands,
        game_assets: Res<GameAssets>,
        // scenes: ResMut<Scene>,
){
    info!("loading");
  
    commands.spawn((
        SceneBundle {
            scene: game_assets.world.clone(),
            ..default()
        },
        bevy::prelude::Name::from("world"),
        GameWorldTag,
        InGameRunning
    ));
    
    /*commands.spawn((
        DynamicSceneBundle {
            scene: asset_server.load(NEW_SCENE_FILE_PATH),
            ..default()
        },
        Hackish
    ));*/
    /*commands.spawn(DynamicSceneBundle {
        // Scenes are loaded just like any other asset.
        scene: asset_server.load(NEW_SCENE_FILE_PATH),
        ..default()
    });*/  
}

use std::io::Read;
use bevy::scene::serde::SceneDeserializer;
use ron::Deserializer;
use serde::de::DeserializeSeed;


#[derive(Debug, Deserialize)]
struct Components2;

#[derive(Debug, Deserialize)]
struct Fake {
    resources: HashMap<u32, String>,
    entities: HashMap<u32, Components2>
}

fn ron_test(){
    let full_path = "/home/ckaos/projects/grappling-boom-bot/assets/save.ron";
    match File::open(full_path) {
        Ok(mut file) => {
            let mut serialized_scene = Vec::new();
            if let Err(why) = file.read_to_end(&mut serialized_scene) {
                error!("file read failed: {why:?}");
            }
            match Deserializer::from_bytes(&serialized_scene) {
                Ok(mut deserializer) => {
                    // deserializer.
                    let bla:Fake = ron::from_str("(
                        resources: {},
                        entities: {}
                    )").unwrap();
                    info!("testing {:?}", bla);
                    info!("YOYO DONE YO !")
                }
                Err(why) => {
                    error!("deserializer creation failed: {why:?}");
                }
            }
        }
        Err(why) => {
            error!("load failed: {why:?}");
        }
    }
}

fn inject_component_data(world: &mut World, scene: DynamicScene){
    let mut entity_map = EntityMap::default();
    if let Err(why) = scene.write_to_world(world, &mut entity_map) {
        panic!("world write failed: {why:?}");
    }
    println!("entity map {:?}", entity_map);
    // TODO: EntityMap doesn't implement `iter()`
    for old_entity in entity_map.keys() {
        let entity = entity_map.get(old_entity).unwrap();
        info!("entity update required: {old_entity:?} -> {entity:?}");
        let e_mut = world
            .entity_mut(entity);           
    }

    info!("done loading scene");
}

fn post_load(world: &mut World){
    let full_path = "/home/ckaos/projects/grappling-boom-bot/assets/save.ron";
    match File::open(full_path) {
        Ok(mut file) => {
            let mut serialized_scene = Vec::new();
            if let Err(why) = file.read_to_end(&mut serialized_scene) {
                error!("file read failed: {why:?}");
            }
            match Deserializer::from_bytes(&serialized_scene) {
                Ok(mut deserializer) => {
                    let result = SceneDeserializer {
                        type_registry: &world.resource::<AppTypeRegistry>().read(),
                    }
                    .deserialize(&mut deserializer);
                    info!("deserialize done");
                    match result {
                        Ok(scene) => {
                            info!("scene loaded");
                            // scene.write_to_world(world, entity_map)
                            //  println!("{:?}", scene.entities);
                            inject_component_data(world, scene);
                            /*for dyn_ent in scene.entities.iter(){
                                // let mut query = scene.world.query::<(Entity, &Name, &GltfExtras, &Parent)>();
                            }*/
                        }
                        Err(why) => {
                            error!("deserialization failed: {why:?}");
                        }
                    }
                }
                Err(why) => {
                    error!("deserializer creation failed: {why:?}");
                }
            }
        }
        Err(why) => {
            error!("load failed: {why:?}");
        }
    }

}
/* 
fn save_scene_system(world: &mut World) {
    // Scenes can be created from any ECS World.
    // You can either create a new one for the scene or use the current World.
    // For demonstration purposes, we'll create a new one.
    let mut scene_world = World::new();

    // The `TypeRegistry` resource contains information about all registered types (including components).
    // This is used to construct scenes, so we'll want to ensure that our previous type registrations
    // exist in this new scene world as well.
    // To do this, we can simply clone the `AppTypeRegistry` resource.
    let type_registry = world.resource::<AppTypeRegistry>().clone();
    scene_world.insert_resource(type_registry);

    let mut component_b = ComponentB::from_world(world);
    component_b.value = "hello".to_string();
    scene_world.spawn((
        component_b,
        ComponentA { x: 1.0, y: 2.0 },
        Transform::IDENTITY,
    ));
    scene_world.spawn(ComponentA { x: 3.0, y: 4.0 });
    scene_world.insert_resource(ResourceA { score: 1 });

    // With our sample world ready to go, we can now create our scene:
    let scene = DynamicScene::from_world(&scene_world);

    // Scenes can be serialized like this:
    let type_registry = world.resource::<AppTypeRegistry>();
    let serialized_scene = scene.serialize_ron(type_registry).unwrap();

    // Showing the scene in the console
    info!("{}", serialized_scene);

    // Writing the scene to a new file. Using a task to avoid calling the filesystem APIs in a system
    // as they are blocking
    // This can't work in WASM as there is no filesystem access
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
*/

fn should_save(
    keycode: Res<Input<KeyCode>>,
) -> bool {
    return keycode.just_pressed(KeyCode::S)
}

fn should_load(
    keycode: Res<Input<KeyCode>>,
) -> bool {
    return keycode.just_pressed(KeyCode::L)
}

use std::fs::File;
use std::io::Write;

use bevy::prelude::*;
use bevy::prelude::{App, Plugin, IntoSystemConfigs};
use bevy::tasks::IoTaskPool;
use bevy::utils::{HashMap, Uuid};

use crate::assets::GameAssets;
use crate::core::spawning::clone_entity::CloneEntity;
use crate::game::{Player, Pickable};
use crate::state::{AppState, InGameRunning};
use crate::test_components::BlueprintName;

use super::GameWorldTag;


const SCENE_FILE_PATH: &str = "save.scn.ron";

#[derive(Component, Debug, )]
pub struct TempLoadedSceneMarker;


#[derive(Component, Debug, )]
pub struct SaveablesToRemove(Vec<(Entity, Name)>);

fn load_saved_scene(
    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,

    mut commands: Commands, 
    asset_server: Res<AssetServer>
) {
    //let world = game_world.single_mut();
    // let world = world.1[0]; // FIXME: dangerous hack because our gltf data have a single child like this, but might not always be the case
    // "Spawning" a scene bundle creates a new entity and spawns new instances
    // of the given scene's entities as children of that entity.

    let child_scene = commands.spawn(
    (
        DynamicSceneBundle {
            // Scenes are loaded just like any other asset.
            scene: asset_server.load(SCENE_FILE_PATH),
            ..default()
        },
        TempLoadedSceneMarker
    )).id();
    // commands.entity(world).add_child(child_scene);
}

fn process_loaded_scene(
    entities: Query<(Entity, &Children), With<TempLoadedSceneMarker>>,
    named_entities: Query<(Entity, &Name, &Parent)>, // FIXME: very inneficient
    mut commands: Commands, 

    saveables: Query<(Entity, &Name), With<Saveable>>
){
    for (entity, children) in entities.iter(){
        let mut entities_to_load:Vec<(Entity, Name)> = vec![];

        for saved_source in children.iter() {
           if let Ok((source, name, _)) = named_entities.get(*saved_source) {
            println!("AAAAAAA {}", name);
            entities_to_load.push((source, name.clone()));

            for (e, n, p) in named_entities.iter(){
                if e != source && name.as_str() == n.as_str(){
                    println!("found entity with same name {} {} {:?} {:?}", name, n, source, e);
                    // source is entity within the newly loaded scene (source), e is within the existing world (destination)
                    info!("copying data from {:?} to {:?}", source, e);
                    commands.add(CloneEntity {
                        source: source,
                        destination: e,
                    });
                    // FIXME: issue with hierarchy & parenting, would be nice to be able to filter out components from CloneEntity
                    commands.entity(p.get()).add_child(e);
                    commands.entity(source).despawn_recursive();

                }
            }
           }
        }
        commands.spawn(SaveablesToRemove(entities_to_load.clone()));
        
       
       
        // if an entity is present in the world but NOT in the saved entities , it should be removed from the world
        // ideally this should be run between spawning of the world/level AND spawn_placeholders

        commands.entity(entity).despawn_recursive();
    }
    /*for saveable in saveables.iter(){
        println!("SAVEABLE {:?}", saveable)
    }*/
}

fn final_cleanup(
    saveables_to_remove: Query<&SaveablesToRemove>,
    mut commands: Commands, 
    saveables: Query<(Entity, &Name), With<Saveable>>
){
    if let Ok(entities_to_load) = saveables_to_remove.get_single()
    {
        for (e, n) in saveables.iter(){
            let mut found = false;
            println!("SAVEABLE {}", n);
    
            //let entities_to_load = saveables_to_remove.single();
            for (en, na) in entities_to_load.0.iter(){
                found = na.as_str() == n.as_str();
                if found {
                    break;
                }
            }
            if !found {
                println!("REMOVING THIS ONE {}", n);
                commands.entity(e).despawn_recursive();
            }
        }
        // if there is a saveable that is NOT in the list of entities to load, despawn it
    }
    
}

fn process_loaded_scene_load_alt(
    entities: Query<(Entity, &Children), With<TempLoadedSceneMarker>>,
    named_entities: Query<(Entity, &Name, &Parent)>, // FIXME: very inneficient
    mut commands: Commands, 

){
    for (entity, children) in entities.iter(){
        let mut entities_to_load:Vec<(Entity, Name)> = vec![];
        for saved_source in children.iter() {
           if let Ok((source, name, _)) = named_entities.get(*saved_source) {
            println!("AAAAAAA {}", name);
            entities_to_load.push((source, name.clone()));
           }
        }
        println!("entities to load {:?}", entities_to_load);

         commands.entity(entity).despawn_recursive();
    }
}

pub struct SaveLoadPlugin;
impl Plugin for SaveLoadPlugin {
  fn build(&self, app: &mut App) {
      app
        .register_type::<Uuid>()
        .register_type::<Saveable>()

        .add_systems(PreUpdate, save_game2.run_if(should_save))
        .add_systems(Update, 

            (
                unload_world,
                load_world,
                load_saved_scene,
                // process_loaded_scene
            )
            .chain()
            .run_if(should_load) // .run_if(in_state(AppState::GameRunning))
        )
         .add_systems(Update,

            (
                process_loaded_scene,
                final_cleanup
            ).chain()
        )



        
        /* .add_systems(PreUpdate, 
            (
                // unload_world,
                // unload_saveables,
                post_load,
                ron_test
            )
            .chain()
            .run_if(should_load)
        )*/

    
      ;
  }
}
