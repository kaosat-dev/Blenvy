use crate::{BlueprintAssetsLoadState, BlueprintAssetsLoaded, BlueprintChildrenReady, BlueprintInfo, BlueprintInstanceReady, InBlueprint, SpawnBlueprint, SubBlueprintsSpawnTracker};
use bevy::asset::{AssetEvent, UntypedAssetId};
use bevy::prelude::*;
use bevy::scene::SceneInstance;
use bevy::utils::hashbrown::HashMap;


/// Resource mapping asset paths (ideally untyped ids, but more complex) to a list of blueprint instance entity ids 
#[derive(Debug, Clone, Resource, Default)]
pub(crate) struct AssetToBlueprintInstancesMapper{
    // pub(crate) untyped_id_to_blueprint_entity_ids: HashMap<UntypedAssetId, Vec<Entity>>
    pub(crate) untyped_id_to_blueprint_entity_ids: HashMap<String, Vec<Entity>>
}

pub(crate) fn react_to_asset_changes(
    mut gltf_events: EventReader<AssetEvent<Gltf>>, // FIXME: Problem: we need to react to any asset change, not just gltf files !
    // mut untyped_events: EventReader<AssetEvent<LoadedUntypedAsset>>,
    blueprint_assets: Query<(
        Entity,
        Option<&Name>,
        &BlueprintInfo,
        Option<&Children>,
    )>,
    // blueprint_children_entities: Query<&InBlueprint>, => can only be used if the entites are tagged, right now that is optional...perhaps do not make it optional
    assets_to_blueprint_instances: Res<AssetToBlueprintInstancesMapper>,

    asset_server: Res<AssetServer>,
    mut commands: Commands,

) {
    for event in gltf_events.read() {
        // LoadedUntypedAsset
        match event {
            AssetEvent::Modified { id } => {
                // React to the gltf file being modified
                // println!("Modified gltf {:?}", asset_server.get_path(*id));
                if let Some(asset_path) = asset_server.get_path(*id) {
                    // let untyped = asset_server.get_handle_untyped(asset_path.clone());
                    // println!("matching untyped handle {:?}", untyped);
                    // let bla = untyped.unwrap().id();
                    // asset_server.get
                    if let Some(entities) = assets_to_blueprint_instances.untyped_id_to_blueprint_entity_ids.get(&asset_path.to_string()) {
                        for entity in entities.iter() {
                            println!("matching blueprint instance {}", entity);
                            if let Ok((entity, entity_name, _blueprint_info, children)) = blueprint_assets.get(*entity) {
                                println!("HOLY MOLY IT DETECTS !!, now respawn {:?}", entity_name);

                                // TODO: only remove those that are "in blueprint"
                                if children.is_some() {
                                    for child in children.unwrap().iter() {
                                        commands.entity(*child).despawn_recursive();
                                    }
                                }
                                commands
                                    .entity(entity)
                                    .remove::<BlueprintInstanceReady>()
                                    .remove::<BlueprintAssetsLoaded>()
                                    .remove::<SceneInstance>()
                                    .remove::<BlueprintAssetsLoadState>()
                                    .remove::<SubBlueprintsSpawnTracker>()
                                    .insert(SpawnBlueprint);
                            }
                        }
                    }
                }
            }
            _ => {}
        }
    }
}
