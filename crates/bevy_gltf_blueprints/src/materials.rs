use std::path::Path;

use bevy::{
    asset::{AssetId, AssetServer, Assets, Handle},
    ecs::{
        component::Component, entity::Entity, query::{Added, With}, reflect::ReflectComponent, system::{Commands, Query, Res, ResMut}
    },
    gltf::Gltf,
    hierarchy::{Children, Parent},
    log::{debug, info},
    pbr::StandardMaterial,
    reflect::Reflect,
    render::mesh::Mesh,
};

use crate::{AssetLoadTracker, AssetsToLoad, BluePrintsConfig};

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// struct containing the name & source of the material to apply
pub struct MaterialInfo {
    pub name: String,
    pub source: String,
}

/// flag component
#[derive(Component)]
pub(crate) struct BlueprintMaterialAssetsLoaded;
/// flag component
#[derive(Component)]
pub(crate) struct BlueprintMaterialAssetsNotLoaded;

/// system that injects / replaces materials from material library
pub(crate) fn materials_inject(
    blueprints_config: ResMut<BluePrintsConfig>,
    material_infos: Query<(Entity, &MaterialInfo), Added<MaterialInfo>>,
    asset_server: Res<AssetServer>,
    mut commands: Commands,
) {
    for (entity, material_info) in material_infos.iter() {
        let model_file_name = format!(
            "{}_materials_library.{}",
            &material_info.source, &blueprints_config.format
        );
        let materials_path = Path::new(&blueprints_config.material_library_folder)
            .join(Path::new(model_file_name.as_str()));
        let material_name = &material_info.name;
        let material_full_path = materials_path.to_str().unwrap().to_string() + "#" + material_name; // TODO: yikes, cleanup

        if blueprints_config
            .material_library_cache
            .contains_key(&material_full_path)
        {
            debug!("material is cached, retrieving");
            blueprints_config
                .material_library_cache
                .get(&material_full_path)
                .expect("we should have the material available");
            commands
                .entity(entity)
                .insert(BlueprintMaterialAssetsLoaded);

        } else {
            let material_file_handle: Handle<Gltf> = asset_server.load(materials_path.clone());
            let material_file_id = material_file_handle.id();
            let mut asset_infos:Vec<AssetLoadTracker<Gltf>> = vec![];

            asset_infos.push(AssetLoadTracker {
                name: material_full_path,
                id: material_file_id,
                loaded: false,
                handle: material_file_handle.clone()
            });
            commands
                .entity(entity)
                .insert(AssetsToLoad{
                    all_loaded: false,
                    asset_infos: asset_infos,
                    progress: 0.0
                    //..Default::default()
                })
                .insert(BlueprintMaterialAssetsNotLoaded);
            /**/
        }
    }
}

// TODO, merge with check_for_loaded, make generic ?
pub(crate) fn check_for_material_loaded(
    mut blueprint_assets_to_load: Query<(Entity, &mut AssetsToLoad<Gltf>),With<BlueprintMaterialAssetsNotLoaded>>,
    asset_server: Res<AssetServer>,
    mut commands: Commands,
){
    for (entity, mut assets_to_load) in blueprint_assets_to_load.iter_mut(){
        let mut all_loaded = true;
        let mut loaded_amount = 0;
        let total = assets_to_load.asset_infos.len();
        for tracker in assets_to_load.asset_infos.iter_mut(){
            let asset_id = tracker.id;
            let loaded = asset_server.is_loaded_with_dependencies(asset_id);
            tracker.loaded = loaded;
            if loaded {
                loaded_amount += 1;
            }else{
                all_loaded = false;
            }
        }
        let progress:f32 = loaded_amount as f32 / total as f32;
        assets_to_load.progress = progress;

        if all_loaded {
            assets_to_load.all_loaded = true;
            commands.entity(entity)
                .insert(BlueprintMaterialAssetsLoaded)
                .remove::<BlueprintMaterialAssetsNotLoaded>();
        }
    }
}


/// system that injects / replaces materials from material library
pub(crate) fn materials_inject2(
    mut blueprints_config: ResMut<BluePrintsConfig>,
    material_infos: Query<(&MaterialInfo, &Children, ), (Added<BlueprintMaterialAssetsLoaded>, With<BlueprintMaterialAssetsLoaded>)>,
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
        let model_file_name = format!(
            "{}_materials_library.{}",
            &material_info.source, &blueprints_config.format
        );
        let materials_path = Path::new(&blueprints_config.material_library_folder)
            .join(Path::new(model_file_name.as_str()));
        let material_name = &material_info.name;

        let material_full_path = materials_path.to_str().unwrap().to_string() + "#" + material_name; // TODO: yikes, cleanup
        let mut material_found: Option<&Handle<StandardMaterial>> = None;

        if blueprints_config
            .material_library_cache
            .contains_key(&material_full_path)
        {
            debug!("material is cached, retrieving");
            let material = blueprints_config
                .material_library_cache
                .get(&material_full_path)
                .expect("we should have the material available");
            material_found = Some(material);
        }else {
            let model_handle: Handle<Gltf> = asset_server.load(materials_path.clone());// FIXME: kinda weird now 
            let mat_gltf = assets_gltf
                .get(model_handle.id())
                .expect("material should have been preloaded");
            if mat_gltf.named_materials.contains_key(material_name) {
                let material = mat_gltf
                    .named_materials
                    .get(material_name)
                    .expect("this material should have been loaded");
                blueprints_config
                    .material_library_cache
                    .insert(material_full_path, material.clone());
                material_found = Some(material);
            }
        }

        if let Some(material) = material_found {
            for child in children.iter() {
                if with_materials_and_meshes.contains(*child) {
                    debug!(
                        "injecting material {}, path: {:?}",
                        material_name,
                        materials_path.clone()
                    );

                    commands.entity(*child).insert(material.clone());
                }
            }
        }
    }
}
