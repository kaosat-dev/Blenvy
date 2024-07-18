use bevy::pbr::DirectionalLightShadowMap;
use bevy::prelude::*;

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
        } else {
            light.shadows_enabled = true;
        }
    }
    for (mut light, blender_light_shadows) in spot_lights.iter_mut() {
        if let Some(blender_light_shadows) = blender_light_shadows {
            light.shadows_enabled = blender_light_shadows.enabled;
        } else {
            light.shadows_enabled = true;
        }
    }

    for (mut light, blender_light_shadows) in point_lights.iter_mut() {
        if let Some(blender_light_shadows) = blender_light_shadows {
            light.shadows_enabled = blender_light_shadows.enabled;
        } else {
            light.shadows_enabled = true;
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
    background_shaders: Query<&BlenderBackgroundShader, Added<BlenderBackgroundShader>>,
    mut commands: Commands,
) {
    for background_shader in background_shaders.iter() {
        commands.insert_resource(AmbientLight {
            color: background_shader.color,
            // Just a guess, see <https://github.com/bevyengine/bevy/issues/12280>
            brightness: background_shader.strength * 400.0,
        });
    }
}
