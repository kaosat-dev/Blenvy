use std::path::Path;

use bevy::{
    asset::{AssetServer, Assets, Handle},
    ecs::{
        component::Component,
        entity::Entity,
        query::{Added, With},
        reflect::ReflectComponent,
        system::{Commands, Query, Res, ResMut},
    },
    gltf::Gltf,
    hierarchy::{Children, Parent},
    log::debug,
    pbr::StandardMaterial,
    reflect::Reflect,
    render::mesh::Mesh,
};

use crate::{AssetLoadTracker, BlenvyAssetsLoadState, BlenvyConfig, BlueprintInstanceReady};

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// struct containing the name & path of the material to apply
pub struct MaterialInfo {
    pub name: String,
    pub path: String,
}

/// flag component
#[derive(Component)]
pub(crate) struct BlueprintMaterialAssetsLoaded;
/// flag component
#[derive(Component)]
pub(crate) struct BlueprintMaterialAssetsNotLoaded;

/// system that injects / replaces materials from material library
pub(crate) fn materials_inject(
    blenvy_config: ResMut<BlenvyConfig>,
    material_infos: Query<(Entity, &MaterialInfo), Added<MaterialInfo>>,
    asset_server: Res<AssetServer>,
    mut commands: Commands,
) {


    for (entity, material_info) in material_infos.iter() {
        println!("Entity with material info {:?} {:?}", entity, material_info);
        let material_full_path = format!("{}#{}", material_info.path, material_info.name);
        if blenvy_config
            .materials_cache
            .contains_key(&material_full_path)
        {
            debug!("material is cached, retrieving");
            blenvy_config
                .materials_cache
                .get(&material_full_path)
                .expect("we should have the material available");
            commands
                .entity(entity)
                .insert(BlueprintMaterialAssetsLoaded);
        } else {
            let material_file_handle = asset_server.load_untyped(&material_info.path.clone()); // : Handle<Gltf> 
            let material_file_id = material_file_handle.id();
            
            let asset_infos: Vec<AssetLoadTracker> = vec![AssetLoadTracker {
                name: material_info.name.clone(),
                path: material_info.path.clone(),
                id: material_file_id,
                loaded: false,
                handle: material_file_handle.clone(),
            }];

            commands
                .entity(entity)
                .insert(BlenvyAssetsLoadState {
                    all_loaded: false,
                    asset_infos,
                    ..Default::default()
                })
                .insert(BlueprintMaterialAssetsNotLoaded);
           
        }
    }
}

// TODO, merge with blueprints_check_assets_loading, make generic ?
pub(crate) fn check_for_material_loaded(
    mut blueprint_assets_to_load: Query<
        (Entity, &mut BlenvyAssetsLoadState),
        With<BlueprintMaterialAssetsNotLoaded>,
    >,
    asset_server: Res<AssetServer>,
    mut commands: Commands,
) {
    for (entity, mut assets_to_load) in blueprint_assets_to_load.iter_mut() {
        let mut all_loaded = true;
        let mut loaded_amount = 0;
        let total = assets_to_load.asset_infos.len();
        for tracker in assets_to_load.asset_infos.iter_mut() {
            let asset_id = tracker.id;
            let loaded = asset_server.is_loaded_with_dependencies(asset_id);
            tracker.loaded = loaded;
            if loaded {
                loaded_amount += 1;
            } else {
                all_loaded = false;
            }
        }
        let progress: f32 = loaded_amount as f32 / total as f32;
        assets_to_load.progress = progress;

        if all_loaded {
            assets_to_load.all_loaded = true;
            commands
                .entity(entity)
                .insert(BlueprintMaterialAssetsLoaded)
                .remove::<BlueprintMaterialAssetsNotLoaded>();
        }
    }
}

/// system that injects / replaces materials from material library
pub(crate) fn materials_inject2(
    mut blenvy_config: ResMut<BlenvyConfig>,
    material_infos: Query<
        (&MaterialInfo, &Children),
        (
            Added<BlueprintMaterialAssetsLoaded>,
            With<BlueprintMaterialAssetsLoaded>,
        ),
    >,
    with_materials_and_meshes: Query<
        (),
        (
            With<Parent>,
            With<Handle<StandardMaterial>>,
            With<Handle<Mesh>>,
        ),
    >,
    assets_gltf: Res<Assets<Gltf>>,
    asset_server: Res<AssetServer>,

    mut commands: Commands,
) {
    for (material_info, children) in material_infos.iter() {
        let material_full_path = format!("{}#{}", material_info.path, material_info.name);
        let mut material_found: Option<&Handle<StandardMaterial>> = None;

        if blenvy_config
            .materials_cache
            .contains_key(&material_full_path)
        {
            debug!("material is cached, retrieving");
            let material = blenvy_config
                .materials_cache
                .get(&material_full_path)
                .expect("we should have the material available");
            material_found = Some(material);
        } else {
            let model_handle: Handle<Gltf> = asset_server.load(material_info.path.clone()); // FIXME: kinda weird now
            let mat_gltf = assets_gltf
                .get(model_handle.id())
                .expect("material should have been preloaded");
            if mat_gltf.named_materials.contains_key(&material_info.name as &str) {
                let material = mat_gltf
                    .named_materials
                    .get(&material_info.name as &str)
                    .expect("this material should have been loaded");
                blenvy_config
                    .materials_cache
                    .insert(material_full_path, material.clone());
                material_found = Some(material);
            }
        }

        if let Some(material) = material_found {
            for child in children.iter() {
                if with_materials_and_meshes.contains(*child) {
                    debug!(
                        "injecting material {}, path: {:?}",
                        material_info.name,
                        material_info.path.clone()
                    );

                    commands.entity(*child).insert(material.clone());
                }
            }
        }
    }
}
