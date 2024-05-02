use bevy::pbr::DirectionalLightShadowMap;
use bevy::prelude::*;
use bevy::render::render_asset::RenderAssetUsages;
use bevy::render::render_resource::{
    Extent3d, TextureDimension, TextureFormat, TextureViewDescriptor, TextureViewDimension,
};
use std::iter;

use crate::GltfComponentsSet;

pub(crate) fn plugin(app: &mut App) {
    app.register_type::<BlenderBackgroundShader>()
        .register_type::<BlenderShadowSettings>()
        .register_type::<BlenderLightShadows>()
        .add_systems(
            Update,
            (process_lights, process_shadowmap, process_background_shader)
                .after(GltfComponentsSet::Injection),
        );
}

#[derive(Component, Reflect, Default, Debug, PartialEq, Clone)]
#[reflect(Component)]
#[non_exhaustive]
/// The properties of a light's shadow , to enable controlling per light shadows from Blender
pub struct BlenderLightShadows {
    pub enabled: bool,
    pub buffer_bias: f32,
}

/// The background color as described by Blender's [background shader](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/background.html).
#[derive(Component, Reflect, Default, Debug, PartialEq, Clone)]
#[reflect(Component)]
#[non_exhaustive]
pub struct BlenderBackgroundShader {
    pub color: Color,
    pub strength: f32,
}

/// The settings used by EEVEE's [shadow rendering](https://docs.blender.org/manual/en/latest/render/eevee/render_settings/shadows.html).
#[derive(Component, Reflect, Default, Debug, PartialEq, Clone)]
#[reflect(Component)]
#[non_exhaustive]
pub struct BlenderShadowSettings {
    pub cascade_size: usize,
}

fn process_lights(
    mut directional_lights: Query<
        (&mut DirectionalLight, Option<&BlenderLightShadows>),
        Added<DirectionalLight>,
    >,
    mut spot_lights: Query<(&mut SpotLight, Option<&BlenderLightShadows>), Added<SpotLight>>,
    mut point_lights: Query<(&mut PointLight, Option<&BlenderLightShadows>), Added<PointLight>>,
) {
    for (mut light, blender_light_shadows) in directional_lights.iter_mut() {
        if let Some(blender_light_shadows) = blender_light_shadows {
            light.shadows_enabled = blender_light_shadows.enabled;
        }
    }
    for (mut light, blender_light_shadows) in spot_lights.iter_mut() {
        if let Some(blender_light_shadows) = blender_light_shadows {
            light.shadows_enabled = blender_light_shadows.enabled;
        }
    }

    for (mut light, blender_light_shadows) in point_lights.iter_mut() {
        if let Some(blender_light_shadows) = blender_light_shadows {
            light.shadows_enabled = blender_light_shadows.enabled;
        }
    }
}

fn process_shadowmap(
    shadowmaps: Query<&BlenderShadowSettings, Added<BlenderShadowSettings>>,
    mut commands: Commands,
) {
    for shadowmap in shadowmaps.iter() {
        commands.insert_resource(DirectionalLightShadowMap {
            size: shadowmap.cascade_size,
        });
    }
}

fn process_background_shader(
    background_shaders: Query<Ref<BlenderBackgroundShader>>,
    cameras: Query<(Entity, Ref<Camera3d>)>,
    mut images: ResMut<Assets<Image>>,
    mut commands: Commands,
    mut env_map_handle: Local<Option<Handle<Image>>>,
) {
    let Ok(background_shader) = background_shaders.get_single() else {
        return;
    };

    let env_map_handle = env_map_handle.get_or_insert_with(|| {
        let size = Extent3d {
            width: 1,
            height: 6,
            depth_or_array_layers: 1,
        };
        let dimension = TextureDimension::D2;
        const SIDES_PER_CUBE: usize = 6;
        let data: Vec<_> = iter::repeat(background_shader.color.as_rgba_u8())
            .take(SIDES_PER_CUBE)
            .flatten()
            .collect();
        let format = TextureFormat::Rgba8UnormSrgb;
        let asset_usage = RenderAssetUsages::RENDER_WORLD;

        let mut image = Image::new(size, dimension, data, format, asset_usage);

        // Source: https://github.com/bevyengine/bevy/blob/85b488b73d6f6e75690962fba67a144d9beb6b88/examples/3d/skybox.rs#L152-L160
        image.reinterpret_stacked_2d_as_array(image.height() / image.width());
        image.texture_view_descriptor = Some(TextureViewDescriptor {
            dimension: Some(TextureViewDimension::Cube),
            ..default()
        });

        images.add(image)
    });
    // Don't need the handle to be &mut
    let env_map_handle = &*env_map_handle;

    if background_shader.is_added() {
        // We're using an environment map, so we don't need the ambient light
        commands.remove_resource::<AmbientLight>();
    }

    let is_bg_outdated = background_shader.is_changed();
    if is_bg_outdated {
        let color = background_shader.color * background_shader.strength;
        commands.insert_resource(ClearColor(color));
    }
    let camera_entities = cameras
        .iter()
        .filter_map(|(entity, cam)| (is_bg_outdated || cam.is_changed()).then_some(entity));

    for camera_entity in camera_entities {
        // See https://github.com/KhronosGroup/glTF-Blender-IO/blob/8573cc0dfb612091bfc1bcf6df55c18a44b9668a/addons/io_scene_gltf2/blender/com/gltf2_blender_conversion.py#L19
        const PBR_WATTS_TO_LUMENS: f32 = 683.0;
        commands.entity(camera_entity).insert(EnvironmentMapLight {
            diffuse_map: env_map_handle.clone(),
            specular_map: env_map_handle.clone(),
            intensity: background_shader.strength * PBR_WATTS_TO_LUMENS,
        });
    }
}
