use bevy::core_pipeline::tonemapping::Tonemapping;
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

use crate::core::camera_tracking::CameraTrackingOffset;
use crate::core::save_load::Dynamic;
use crate::game::{Pickable, Player};


#[derive(Event, Debug)]
pub struct SaveRequest {
    pub path: String,
}

pub fn should_save(
    save_requests: EventReader<SaveRequest>,
) -> bool {
    return save_requests.len() > 0;
}

pub fn prepare_save_game(
    saveables: Query<(Entity), (With<Dynamic>, With<BlueprintName>)>,
    mut commands: Commands,
){
    for entity in saveables.iter(){
        println!("PREPARING SAVE");
        // TODO: only do this for entities with blueprints
        commands.entity(entity).insert(SpawnHere);
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
    println!("SAVING TO {}", save_path);
    events.clear(); 

    let saveable_entities: Vec<Entity> = world
        .query_filtered::<Entity, (With<Dynamic>, Without<InBlueprint>)>()
        .iter(world)
        .collect();


    println!("saveable entities {}", saveable_entities.len());

    let foo = world
    .query_filtered::<Entity, (With<Dynamic>, Without<InBlueprint>)>()
    .iter(world);

   
    let components = HashSet::from([
        TypeId::of::<Name>(),
        TypeId::of::<Transform>(), 
        TypeId::of::<Velocity>() , 
        TypeId::of::<BlueprintName>(),
        TypeId::of::<SpawnHere>(),
        TypeId::of::<Dynamic>(),

        // TypeId::of::<Parent>(),
        // TypeId::of::<Children>(),
        TypeId::of::<InheritedVisibility>(),

        


        TypeId::of::<Camera>(),
        TypeId::of::<Camera3d>(),
        TypeId::of::<Tonemapping>(),
        TypeId::of::<CameraTrackingOffset>(),
        TypeId::of::<Projection>(),
        TypeId::of::<CameraRenderGraph>(),
        TypeId::of::<Frustum>(),
        TypeId::of::<GlobalTransform>(),
        TypeId::of::<VisibleEntities>(),

        TypeId::of::<Pickable>(),



        ]);

    let filter = SceneFilter::Allowlist(components);
        

    let mut scene_builder = DynamicSceneBuilder::from_world(world).with_filter(filter.clone());


    let dyn_scene = scene_builder
        
        /* .allow::<Transform>()
        .allow::<Velocity>()
        .allow::<BlueprintName>()*/

        /* .deny::<Children>()
        .deny::<Parent>()
        .deny::<InheritedVisibility>()
        .deny::<Visibility>()
        .deny::<GltfExtras>()
        .deny::<GlobalTransform>()
        .deny::<Collider>()
        .deny::<RigidBody>()
        .deny::<Saveable>()
        // camera stuff
        .deny::<Camera>()
        .deny::<CameraRenderGraph>()
        .deny::<Camera3d>()
        .deny::<Clusters>()
        .deny::<VisibleEntities>()
        .deny::<VisiblePointLights>()
        //.deny::<HasGizmoMarker>()
        */
        .extract_entities(saveable_entities.into_iter())
        .build();

    let serialized_scene = dyn_scene
        .serialize_ron(world.resource::<AppTypeRegistry>())
        .unwrap();

    #[cfg(not(target_arch = "wasm32"))]
    IoTaskPool::get()
        .spawn(async move {
            // Write the scene RON data to file
            File::create(format!("assets/scenes/{save_path}"))
                .and_then(|mut file| file.write(serialized_scene.as_bytes()))
                .expect("Error while writing scene to file");
        })
        .detach();
}
