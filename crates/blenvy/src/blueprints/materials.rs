use bevy::prelude::*;

use crate::BlenvyConfig;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// struct containing the name & path of the material to apply
pub struct MaterialInfo {
    pub name: String,
    pub path: String,
}

#[derive(Component, Default, Debug)]
pub struct MaterialProcessed;

/// system that injects / replaces materials from material library
pub(crate) fn inject_materials(
    mut blenvy_config: ResMut<BlenvyConfig>,
    material_infos: Query<
        (Entity, &MaterialInfo, &Children),
        Without<MaterialProcessed>, // (With<BlueprintReadyForPostProcess>)
                                    /*(
                                        Added<BlueprintMaterialAssetsLoaded>,
                                        With<BlueprintMaterialAssetsLoaded>,
                                    ),*/
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
    for (entity, material_info, children) in material_infos.iter() {
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
            let mat_gltf = assets_gltf.get(model_handle.id()).unwrap_or_else(|| panic!("materials file {} should have been preloaded", material_info.path));
            if mat_gltf
                .named_materials
                .contains_key(&material_info.name as &str)
            {
                let material = mat_gltf
                    .named_materials
                    .get(&material_info.name as &str)
                    .expect("this material should have been loaded at this stage, please make sure you are correctly preloading them");
                blenvy_config
                    .materials_cache
                    .insert(material_full_path, material.clone());
                material_found = Some(material);
            }
        }

        commands.entity(entity).insert(MaterialProcessed);

        if let Some(material) = material_found {
            for child in children.iter() {
                if with_materials_and_meshes.contains(*child) {
                    info!(
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
