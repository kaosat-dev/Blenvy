use std::path::Path;

use bevy::{
    asset::{AssetServer, Assets, Handle},
    ecs::{
        component::Component,
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

use crate::BluePrintsConfig;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// struct containing the name & source of the material to apply
pub struct MaterialInfo {
    pub name: String,
    pub source: String,
}

/// system that injects / replaces materials from material library
pub(crate) fn materials_inject(
    mut blueprints_config: ResMut<BluePrintsConfig>,
    material_infos: Query<(&MaterialInfo, &Children), Added<MaterialInfo>>,
    with_materials_and_meshes: Query<(), (
        With<Parent>,
        With<Handle<StandardMaterial>>,
        With<Handle<Mesh>>,
    )>,
    models: Res<Assets<bevy::gltf::Gltf>>,

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
        } else {
            let my_gltf: Handle<Gltf> = asset_server.load(materials_path.clone());
            let mat_gltf = models
                .get(my_gltf.id())
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
