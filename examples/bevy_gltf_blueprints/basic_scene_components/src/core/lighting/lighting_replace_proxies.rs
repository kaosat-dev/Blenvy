use bevy::prelude::*;

use bevy::pbr::{CascadeShadowConfig, CascadeShadowConfigBuilder};


#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct AmbientLightP {pub color: Color, pub brightness: f32}

pub fn lighting_replace_proxies(
    mut added_dirights: Query<(Entity, &mut DirectionalLight), Added<DirectionalLight>>,
    mut added_spotlights: Query<&mut SpotLight, Added<SpotLight>>,
    added_ambient_proxies : Query<&AmbientLightP>,
    mut commands: Commands,
) {
    for (entity, mut light) in added_dirights.iter_mut() {
        light.illuminance *= 5.0;
        light.shadows_enabled = true;
        let shadow_config: CascadeShadowConfig = CascadeShadowConfigBuilder {
            first_cascade_far_bound: 15.0,
            maximum_distance: 135.0,
            ..default()
        }
        .into();
        commands.entity(entity).insert(shadow_config);
    }
    for mut light in added_spotlights.iter_mut() {
        light.shadows_enabled = true;
    }

    for ambient in added_ambient_proxies.iter(){
        commands.insert_resource(AmbientLight {
            color: ambient.color,
            brightness: ambient.brightness,
        });
    }
}
