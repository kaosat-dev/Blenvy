use bevy::{prelude::{info, ResMut}, input::{keyboard::KeyCode, Input}, ecs::system::Res};
use bevy_rapier3d::{prelude::RapierConfiguration, render::DebugRenderContext};

pub fn pause_physics(mut physics_config: ResMut<RapierConfiguration>) {
    info!("pausing physics");
    physics_config.physics_pipeline_active = false;
}

pub fn resume_physics(mut physics_config: ResMut<RapierConfiguration>) {
    info!("unpausing physics");
    physics_config.physics_pipeline_active = true;
}

pub fn toggle_physics_debug(
    mut debug_config: ResMut<DebugRenderContext>,
    keycode: Res<Input<KeyCode>>,
) {
    if keycode.just_pressed(KeyCode::D) {
        debug_config.enabled = !debug_config.enabled;
    }
}
