use bevy::{
    prelude::{info, ResMut},
    time::Time,
};
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
