use crate::{BlueprintAssetsLoadState, BlueprintAssetsLoaded, BlueprintInfo, SpawnBlueprint};
use bevy::asset::AssetEvent;
use bevy::prelude::*;
use bevy::scene::SceneInstance;

pub(crate) fn react_to_asset_changes(
    mut gltf_events: EventReader<AssetEvent<Gltf>>,
    // mut untyped_events: EventReader<AssetEvent<LoadedUntypedAsset>>,
    mut blueprint_assets: Query<(
        Entity,
        Option<&Name>,
        &BlueprintInfo,
        &mut BlueprintAssetsLoadState,
        Option<&Children>,
    )>,
    asset_server: Res<AssetServer>,
    mut commands: Commands,
) {
    for event in gltf_events.read() {
        // LoadedUntypedAsset
        match event {
            AssetEvent::Modified { id } => {
                // React to the image being modified
                // println!("Modified gltf {:?}", asset_server.get_path(*id));
                for (entity, entity_name, _blueprint_info, mut assets_to_load, children) in
                    blueprint_assets.iter_mut()
                {
                    for tracker in assets_to_load.asset_infos.iter_mut() {
                        if asset_server.get_path(*id).is_some() {
                            if tracker.path == asset_server.get_path(*id).unwrap().to_string() {
                                println!("HOLY MOLY IT DETECTS !!, now respawn {:?}", entity_name);
                                if children.is_some() {
                                    for child in children.unwrap().iter() {
                                        commands.entity(*child).despawn_recursive();
                                    }
                                }
                                commands
                                    .entity(entity)
                                    .remove::<BlueprintAssetsLoaded>()
                                    .remove::<SceneInstance>()
                                    .remove::<BlueprintAssetsLoadState>()
                                    .insert(SpawnBlueprint);

                                break;
                            }
                        }
                    }
                }
            }
            _ => {}
        }
    }
}
