use bevy::prelude::*;
use bevy::tasks::IoTaskPool;
use bevy_gltf_blueprints::{BlueprintName, InBlueprint, SpawnHere};

use std::fs::{self, File};
use std::io::Write;
use std::path::Path;

use crate::{Dynamic, DynamicEntitiesRoot, SaveLoadConfig, StaticWorldMarker};

#[derive(Event, Debug)]
pub struct SaveRequest {
    pub path: String,
}

#[derive(Event)]
pub struct SavingFinished;

pub fn should_save(save_requests: EventReader<SaveRequest>) -> bool {
    return save_requests.len() > 0;
}

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
/// marker component for entities that do not have parents, or whose parents should be ignored when serializing
pub(crate) struct RootEntity;

#[derive(Component, Debug)]
pub(crate) struct OriginalParent(pub(crate) Entity);

// any child of dynamic/ saveable entities that is not saveable itself should be removed from the list of children
pub fn prepare_save_game(
    saveables: Query<(Entity), (With<Dynamic>, With<BlueprintName>)>,
    root_entities: Query<Entity, Or<(With<DynamicEntitiesRoot>, Without<Parent>)>>, //  With<DynamicEntitiesRoot>
    dynamic_entities: Query<(Entity, &Parent, Option<&Children>), With<Dynamic>>,
    mut commands: Commands,

    names: Query<&Name>

) {
    for entity in saveables.iter() {
        commands.entity(entity).insert(SpawnHere);
    }

    for (entity, parent, children) in dynamic_entities.iter() {
        let parent = parent.get();
        if root_entities.contains(parent) {
            commands.entity(entity).insert(RootEntity);
        }

        if let Some(children) = children {
            for sub_child in children.iter(){
                if !dynamic_entities.contains(*sub_child){
                    println!("uh OH {:?}", names.get(*sub_child));
                    commands.entity(*sub_child).insert(OriginalParent(entity));
                    commands.entity(entity).remove_children(&[*sub_child]);
                }
            }
        }
    }
}
pub fn save_game(world: &mut World) {
    info!("saving");

    let mut save_path: String = "".into();
    let mut events = world.resource_mut::<Events<SaveRequest>>();

    for event in events.get_reader().read(&events) {
        info!("SAVE EVENT !! {:?}", event);
        save_path = event.path.clone();
    }
    events.clear();

    let saveable_entities: Vec<Entity> = world
        .query_filtered::<Entity, (With<Dynamic>, Without<InBlueprint>, Without<RootEntity>)>()
        .iter(world)
        .collect();

    let saveable_root_entities: Vec<Entity> = world
        .query_filtered::<Entity, (With<Dynamic>, Without<InBlueprint>, With<RootEntity>)>()
        .iter(world)
        .collect();

    let static_world_markers: Vec<Entity> = world
        .query_filtered::<Entity, (With<StaticWorldMarker>)>()
        .iter(world)
        .collect();

    println!("saveable entities {}", saveable_entities.len());
    println!("saveable root entities {}", saveable_root_entities.len());
    println!(
        "saveable static_world_markers {}",
        static_world_markers.len()
    );

    let save_load_config = world
        .get_resource::<SaveLoadConfig>()
        .expect("SaveLoadConfig should exist at this stage");

    // we hardcode some of the always allowed types
    let filter = save_load_config
        .entity_filter
        .clone()
        .allow::<Parent>()
        .allow::<Children>()
        .allow::<BlueprintName>()
        .allow::<SpawnHere>()
        .allow::<Dynamic>()
        .allow::<StaticWorldMarker>();

    // for root entities, it is the same EXCEPT we make sure parents are not included
    let filter_root = filter.clone().deny::<Parent>();

    // for default stuff
    let scene_builder = DynamicSceneBuilder::from_world(world).with_filter(filter.clone());

    let mut dyn_scene = scene_builder
        .extract_entities(saveable_entities.clone().into_iter())
        .remove_empty_entities()
        .build();

    // for root entities
    let scene_builder_root =
        DynamicSceneBuilder::from_world(world).with_filter(filter_root.clone());

    let mut dyn_scene_root = scene_builder_root
        .extract_entities(
            saveable_root_entities
                .clone()
                .into_iter()
                .chain(static_world_markers.into_iter()),
        )
        .remove_empty_entities()
        .build();

    dyn_scene.entities.append(&mut dyn_scene_root.entities);

    let serialized_scene = dyn_scene
        .serialize_ron(world.resource::<AppTypeRegistry>())
        .unwrap();

    let save_path = Path::new("assets")
        .join(&save_load_config.save_path)
        .join(Path::new(save_path.as_str())); // Path::new(&save_load_config.save_path).join(Path::new(save_path.as_str()));
    println!("SAVING TO {:?}", save_path);

    // world.send_event(SavingFinished);

    #[cfg(not(target_arch = "wasm32"))]
    let foo = IoTaskPool::get()
        .spawn(async move {
            // Write the scene RON data to file
            File::create(save_path)
                .and_then(|mut file| file.write(serialized_scene.as_bytes()))
                .expect("Error while writing save to file");
        })
        .detach();
    println!("foo , {:?}", foo);

    /*let mut query = world.query::<(Entity, &OriginalParent)>();
    for (entity, original_parent) in query.iter(world) {
        world.entity_mut(original_parent.0).add_child(entity);
    }*/
}


pub(crate) fn cleanup_save(
    needs_parent_reset: Query<(Entity, &OriginalParent)>,
    mut saving_finished: EventWriter<SavingFinished>,
    mut commands: Commands,
){
    for (entity, original_parent) in needs_parent_reset.iter(){
        println!("resetting parent");
        commands.entity(original_parent.0).add_child(entity);
    }
    saving_finished.send(SavingFinished);
}