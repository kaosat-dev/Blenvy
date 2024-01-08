use bevy::core_pipeline::tonemapping::Tonemapping;
use bevy::ecs::component::ComponentIdFor;
use bevy::ecs::storage::Table;
use bevy::render::camera::CameraRenderGraph;
use bevy::render::primitives::Frustum;
use bevy::render::view::VisibleEntities;
use bevy::tasks::IoTaskPool;
use bevy::utils::HashSet;
use bevy::prelude::*;
use bevy_gltf_blueprints::{BlueprintName, SpawnHere, InBlueprint};
use bevy_rapier3d::dynamics::Velocity;

use std::any::{TypeId};
use std::fs::{File, self};
use std::io::Write;
use std::path::Path;

use crate::core::camera_tracking::CameraTrackingOffset;
use crate::core::save_load::{Dynamic, SaveLoadConfig};
use crate::game::{Pickable, Player, DynamicEntitiesRoot};


#[derive(Event, Debug)]
pub struct SaveRequest {
    pub path: String,
}

pub fn should_save(
    save_requests: EventReader<SaveRequest>,
) -> bool {
    return save_requests.len() > 0;
}

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct RootEntity;

pub fn prepare_save_game(
    saveables: Query<(Entity), (With<Dynamic>, With<BlueprintName>)>,
    dynamic_entities: Query<Entity, Or<(With<DynamicEntitiesRoot>, Without<Parent>)>>, //  With<DynamicEntitiesRoot>  
    children_of_world: Query<(Entity, &Parent), With<Dynamic> >,
    mut commands: Commands,
){
    for entity in saveables.iter(){
        commands.entity(entity).insert(SpawnHere);
    }

    for (child, parent) in children_of_world.iter(){
        let parent = parent.get();
        if dynamic_entities.contains(parent) {
            commands.entity(child).insert(RootEntity);
        }
    }
}
pub fn save_game(
    world: &mut World,
) {
    info!("saving");


    let mut save_path:String = "".into();
    let mut events = world
        .resource_mut::<Events<SaveRequest>>();

    for event in events.get_reader().read(&events) {
        info!("SAVE EVENT !! {:?}", event);
        save_path = event.path.clone();
    }
    events.clear(); 

    let saveable_entities: Vec<Entity> = world
        .query_filtered::<Entity, (With<Dynamic>, Without<InBlueprint>, Without<RootEntity>)>()
        .iter(world)
        .collect();


    println!("saveable entities {}", saveable_entities.len());

    let saveable_root_entities: Vec<Entity>  = world
    .query_filtered::<Entity, (With<Dynamic>, Without<InBlueprint>, With<RootEntity>)>()
    .iter(world)
    .collect();
    println!("saveable root entities {}", saveable_root_entities.len());

   
    let save_load_config = world.get_resource::<SaveLoadConfig>().expect("SaveLoadConfig should exist at this stage");

    // we hardcode some of the always allowed types
    let filter = save_load_config.entity_filter.clone()
        .allow::<Parent>()
        .allow::<Children>()
        .allow::<BlueprintName>()
        .allow::<SpawnHere>()
        .allow::<Dynamic>()
    ;

    // for root entities, it is the same EXCEPT we make sure parents are not included
    let filter_root = filter.clone()
        .deny::<Parent>();


    // for default stuff
    let scene_builder = DynamicSceneBuilder::from_world(world).with_filter(filter.clone());

    let mut dyn_scene = scene_builder
        .extract_entities(saveable_entities.clone().into_iter() )
        .remove_empty_entities()
        .build();

    // for root entities
    let scene_builder_root = DynamicSceneBuilder::from_world(world).with_filter(filter_root.clone());

    let mut dyn_scene_root = scene_builder_root
        .extract_entities(saveable_root_entities.clone().into_iter() )
        .remove_empty_entities()
        .build();
    
    dyn_scene.entities.append(&mut dyn_scene_root.entities);

    let serialized_scene = dyn_scene
        .serialize_ron(world.resource::<AppTypeRegistry>())
        .unwrap();


    let save_path =  Path::new("assets").join(&save_load_config.save_path).join(Path::new(save_path.as_str())); // Path::new(&save_load_config.save_path).join(Path::new(save_path.as_str()));
    println!("SAVING TO {:?}", save_path);

    #[cfg(not(target_arch = "wasm32"))]
    IoTaskPool::get()
        .spawn(async move {
            // Write the scene RON data to file
            File::create(save_path)
                .and_then(|mut file| file.write(serialized_scene.as_bytes()))
                .expect("Error while writing save to file");
        })
        .detach();
}
