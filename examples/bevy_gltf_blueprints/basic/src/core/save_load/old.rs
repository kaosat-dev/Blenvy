const NEW_SCENE_FILE_PATH:&str="save.scn.ron";




use bevy::ecs::component::Components;
use bevy::ecs::entity::EntityMap;
use serde::{Deserialize, Serialize};


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



#[derive(Component, Reflect, Debug, Default )]
#[reflect(Component)]
pub struct Hackish;



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