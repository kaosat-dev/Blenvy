use bevy::prelude::*;
use blenvy::{BlenvyPlugin, BlueprintInfo, GameWorldTag, HideUntilReady, SpawnBlueprint};

#[derive(Component, Reflect)]
#[reflect(Component)]
pub struct TupleRelations(Entity);

#[derive(Component, Reflect)]
#[reflect(Component)]
pub struct BigRelations {
    main: Entity,
    other: Vec<Entity>,
}

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins.set(AssetPlugin::default()),
            BlenvyPlugin::default(),
        ))
        .register_type::<TupleRelations>()
        .register_type::<BigRelations>()
        .add_systems(Startup, setup_game)
        .run();
}

fn setup_game(mut commands: Commands) {
    // here we actually spawn our game world/level
    commands.spawn((
        BlueprintInfo::from_path("levels/World.glb"), // all we need is a Blueprint info...
        SpawnBlueprint, // and spawnblueprint to tell blenvy to spawn the blueprint now
        HideUntilReady, // only reveal the level once it is ready
        GameWorldTag,
    ));
}
