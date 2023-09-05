use bevy::prelude::*;

use crate::{
    core::spawning::{spawn_entities::GameWorldTag, clone_entity::CloneEntity}, 
    assets::GameAssets, 
    state::{InGameRunning, AppState, GameState}
};

use super::Saveable;


pub fn should_load(
    keycode: Res<Input<KeyCode>>,
) -> bool {
    return keycode.just_pressed(KeyCode::L)
}

pub fn load_prepare(
    mut next_app_state: ResMut<NextState<AppState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
){
    
    next_app_state.set(AppState::LoadingGame);
    next_game_state.set(GameState::None)
}

/// unload the level recursively
pub fn unload_world(world: &mut World) {
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



// almost identical to setup_game, !!??
pub fn load_world(
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
}


const SCENE_FILE_PATH: &str = "save.scn.ron";

#[derive(Component, Debug, )]
pub struct TempLoadedSceneMarker;


#[derive(Component, Debug, )]
pub struct SaveablesToRemove(Vec<(Entity, Name)>);

pub fn load_saved_scene(
    mut commands: Commands, 
    asset_server: Res<AssetServer>
) {
   
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
    info!("loaded saved scene, post processing now");
}

pub fn process_loaded_scene(
    entities: Query<(Entity, &Children), With<TempLoadedSceneMarker>>,
    named_entities: Query<(Entity, &Name, &Parent)>, // FIXME: very inneficient
    mut commands: Commands, 

    saveables: Query<(Entity, &Name), With<Saveable>>
){
    for (entity, children) in entities.iter(){
        let mut entities_to_load:Vec<(Entity, Name)> = vec![];

        for saved_source in children.iter() {
           if let Ok((source, name, _)) = named_entities.get(*saved_source) {
            entities_to_load.push((source, name.clone()));

            for (e, n, p) in named_entities.iter(){
                if e != source && name.as_str() == n.as_str(){
                    // println!("found entity with same name {} {} {:?} {:?}", name, n, source, e);
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
    //for saveable in saveables.iter(){
    //    println!("SAVEABLE BEFORE {:?}", saveable)
    //}
}

pub fn final_cleanup(
    saveables_to_remove: Query<(Entity, &SaveablesToRemove)>,
    mut commands: Commands, 
    saveables: Query<(Entity, &Name), With<Saveable>>
){
    if let Ok((e, entities_to_load)) = saveables_to_remove.get_single()
    {
        info!("saveables to remove {:?}", entities_to_load);
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

        // despawn list
        commands.entity(e).despawn_recursive();
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