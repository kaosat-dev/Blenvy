use bevy::prelude::*;

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
/// component used to mark any entity as Dynamic: aka add this to make sure your entity is going to be saved
pub struct Dynamic(pub bool);

