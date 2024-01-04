use bevy::prelude::*;
use bevy::utils::Uuid;

#[derive(Component, Reflect, Debug)]
#[reflect(Component)]
pub struct Saveable {
    id: Uuid,
}

impl Default for Saveable {
    fn default() -> Self {
        Saveable { id: Uuid::new_v4() }
    }
}


#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct Dynamic(pub bool);