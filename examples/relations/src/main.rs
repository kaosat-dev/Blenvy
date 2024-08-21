use bevy::prelude::*;
use blenvy::{BlenvyPlugin, BlueprintInfo, GameWorldTag, HideUntilReady, SpawnBlueprint};

#[derive(Component, Reflect, Debug)]
#[reflect(Component)]
pub struct TupleRelations(Entity); // TODO: Serialization on blender side currently is broken

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
        .add_systems(Update, (print_names, print_tuple_relations))
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

fn print_names(query: Query<(Entity, &Name), Added<Name>>) {
    for (entity, name) in &query {
        info!("[EXAMPLE] {name} is {entity}");
    }
}

fn print_tuple_relations(query: Query<(&Name, &TupleRelations), Added<TupleRelations>>) {
    for (name, r) in &query {
        info!("[EXAMPLE] {name} has the relation {r:?}")
    }
}
