use bevy::prelude::*;

use crate::{
    core::blueprints::{clone_entity::CloneEntity, SpawnHere, GameWorldTag}, 
    assets::GameAssets, 
    state::{InAppRunning, AppState, GameState}
};

use super::Saveable;

const SCENE_FILE_PATH: &str = "save.scn.ron";

#[derive(Component, Debug, )]
pub struct TempLoadedSceneMarker;

#[derive(Component, Debug, )]
pub struct SaveablesToRemove(Vec<(Entity, Name)>);



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
    next_game_state.set(GameState::None);
    info!("--loading: prepare")
}

/// unload the level recursively
pub fn unload_world_old(world: &mut World) {
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

pub fn unload_world(
    mut commands: Commands,
    gameworlds: Query<Entity, With<GameWorldTag>>
){
    for e in gameworlds.iter(){
        info!("--loading: despawn old world/level");
        commands.entity(e).despawn_recursive();
    }
}

// almost identical to setup_game, !!??
pub fn load_world(
    mut commands: Commands,
        game_assets: Res<GameAssets>,
        // scenes: ResMut<Scene>,
){
    info!("--loading: loading world/level");
  
    commands.spawn((
        SceneBundle {
            scene: game_assets.world.clone(),
            ..default()
        },
        bevy::prelude::Name::from("world"),
        GameWorldTag,
        InAppRunning
    ));
}




pub fn load_saved_scene(
    mut commands: Commands, 
    asset_server: Res<AssetServer>
) {
    commands.spawn(
    (
        DynamicSceneBundle {
            // Scenes are loaded just like any other asset.
            scene: asset_server.load(SCENE_FILE_PATH),
            ..default()
        },
        TempLoadedSceneMarker
    ));
    // commands.entity(world).add_child(child_scene);
    info!("--loading: loaded saved scene");
}

pub fn process_loaded_scene(
    loaded_scene: Query<(Entity, &Children), (With<TempLoadedSceneMarker>)>,
    named_entities: Query<(Entity, &Name, &Parent)>, // FIXME: very inneficient
    mut commands: Commands, 

    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,
    saveables: Query<(Entity, &Name), With<Saveable>>,
    asset_server: Res<AssetServer>
){
    for (loaded_scene, children) in loaded_scene.iter(){
        info!("--loading: post processing loaded scene");

        let mut entities_to_load:Vec<(Entity, Name)> = vec![];

        for loaded_entity in children.iter() {
           if let Ok((source, name, _)) = named_entities.get(*loaded_entity) {
                entities_to_load.push((source, name.clone()));

                let mut found = false;
                for (e, n, p) in named_entities.iter(){
                    // if we have an entity with the same name as in same file, overwrite
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
                        found = true;
                        break;
                    }
                }
                // entity not found in the list of existing entities (ie entities that came as part of the level)
                // so we spawn a new one
                if !found {
                    info!("generating new entity");
                    let world = game_world.single_mut();
                    let world = world.1[0];

                    let new_entity = commands.spawn((
                        bevy::prelude::Name::from(name.clone()),
                        SpawnHere,
                    )).id();

                    commands.add(CloneEntity {
                        source: source,
                        destination: new_entity,
                    });

                    commands.entity(world).add_child(new_entity);
                    info!("copying data from {:?} to {:?}", source, new_entity);

                 
                    
                }

           }
        }
        commands.spawn(SaveablesToRemove(entities_to_load.clone()));
        
       
       
        // if an entity is present in the world but NOT in the saved entities , it should be removed from the world
        // ideally this should be run between spawning of the world/level AND spawn_placeholders

        // remove the dynamic scene
        info!("--loading: DESPAWNING LOADED SCENE");
        commands.entity(loaded_scene).despawn_recursive();

        asset_server.mark_unused_assets();
        asset_server.free_unused_assets();

    }
    //for saveable in saveables.iter(){
    //    println!("SAVEABLE BEFORE {:?}", saveable)
    //}
}

pub fn final_cleanup(
    saveables_to_remove: Query<(Entity, &SaveablesToRemove)>,
    mut commands: Commands, 
    saveables: Query<(Entity, &Name), With<Saveable>>,
    mut next_app_state: ResMut<NextState<AppState>>,
    mut next_game_state: ResMut<NextState<GameState>>,

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

        info!("--loading: done, move to InGame state");
        // next_app_state.set(AppState::AppRunning);
        next_game_state.set(GameState::InGame);
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