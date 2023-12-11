use std::path::Path;

use bevy::{ecs::{query::{Added, With}, system::{Query, Commands, Res}, component::Component, reflect::ReflectComponent}, reflect::Reflect, hierarchy::{Children, Parent}, asset::{Handle, AssetServer, Assets}, pbr::StandardMaterial, render::mesh::Mesh, gltf::Gltf};

use crate::BluePrintsConfig;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// struct containing the name of the material to apply
pub struct MaterialInfo{
    pub name: String,
    pub source: String
}


pub(crate) fn materials_inject(
    blueprints_config: Res<BluePrintsConfig>,
    material_infos: Query<(&MaterialInfo, &Children), Added<MaterialInfo>>,
    with_materials_and_meshes: Query<(With<Parent>, With<Handle<StandardMaterial>>, With<Handle<Mesh>>)>,
    models: Res<Assets<bevy::gltf::Gltf>>,


    asset_server: Res<AssetServer>,
    mut commands: Commands,
){

    for (material_info, children) in material_infos.iter() {
        let model_file_name = format!("{}_materials_library.{}", &material_info.source, &blueprints_config.format);
        let materials_path = Path::new(&blueprints_config.material_library_folder).join(Path::new(model_file_name.as_str()));
        let my_gltf:Handle<Gltf> = asset_server.load(materials_path.clone());
        let mat_gltf = models.get(my_gltf.id()).expect("material should have been preloaded");
        let materials_list = mat_gltf.named_materials.clone();

        let material_name = &material_info.name;
        println!("need to inject material for {}, path: {:?}", material_name, materials_path.clone());
        for child in children.iter() {
            if with_materials_and_meshes.contains(*child) {
                if materials_list.contains_key(material_name) {
                    println!("material found");
                    let material = materials_list.get(material_name).expect("this material should have been loaded");
                    commands
                        .entity(*child)
                        .insert(material.clone());
                }
            }
        }
    }
}
