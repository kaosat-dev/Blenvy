use bevy::ecs::system::Res;
use bevy::gizmos::config::{GizmoConfig, GizmoConfigStore};
use bevy::input::keyboard::KeyCode;
use bevy::input::ButtonInput;
use bevy::log::info;
use bevy::{prelude::ResMut, time::Time};

use bevy_xpbd_3d::prelude::Physics;
use bevy_xpbd_3d::prelude::*;

pub fn pause_physics(mut time: ResMut<Time<Physics>>) {
    info!("pausing physics");
    time.pause();
}

pub fn resume_physics(mut time: ResMut<Time<Physics>>) {
    info!("unpausing physics");
    time.unpause();
}

pub fn toggle_physics_debug(
    mut config_store: ResMut<GizmoConfigStore>,
    keycode: Res<ButtonInput<KeyCode>>,
) {
    if keycode.just_pressed(KeyCode::KeyD) {
        let config = config_store.config_mut::<PhysicsGizmos>().0;
        config.enabled = !config.enabled;
        println!("BLAAA");
        /* 
        .insert_gizmo_group(
            PhysicsGizmos {
                aabb_color: Some(Color::WHITE),
                ..default()
            },
            GizmoConfig::default(),
        )*/
    }
}
