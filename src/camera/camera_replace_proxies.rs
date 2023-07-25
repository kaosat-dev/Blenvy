
use bevy::prelude::*;
use bevy::core_pipeline::bloom::{BloomSettings, BloomCompositeMode};
use bevy::core_pipeline::tonemapping::{Tonemapping, DebandDither};

use super::CameraTracking;

pub fn camera_replace_proxies (
    mut commands: Commands,
    mut added_cameras: Query<(Entity, &mut Camera), (Added<Camera>, With<CameraTracking>)>,
) {

    for (entity, mut camera) in added_cameras.iter_mut(){
        info!("detected added camera, updating proxy");
        camera.hdr = true;
        commands.entity(entity)
          .insert(
            DebandDither::Enabled
          )
          .insert(
            Tonemapping::None
          )
          .insert(
            BloomSettings{
              intensity: 0.08,
              composite_mode:BloomCompositeMode::Additive,
              ..default()
             }
          )
        
          ;
      }
}

