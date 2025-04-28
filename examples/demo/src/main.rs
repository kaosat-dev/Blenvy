use avian3d::prelude::*;
use bevy::prelude::*;
use blenvy::{
    AddToGameWorld, BlenvyPlugin, BluePrintBundle, BlueprintInfo, Dynamic, GameWorldTag,
    HideUntilReady, SpawnBlueprint,
};

mod game;
use game::*;

mod test_components;
use rand::Rng;
use test_components::*;

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins.set(AssetPlugin::default()),
            // our custom plugins
            ComponentsExamplesPlugin, // Showcases different type of components /structs
            BlenvyPlugin::default(),
            GamePlugin,
        ))
        .add_systems(Startup, setup_game)
        .add_systems(Update, spawn_blueprint_instance)
        .run();
}

// this is how you setup & spawn a level from a blueprint
fn setup_game(mut commands: Commands) {
    // here we actually spawn our game world/level
    commands.spawn((
        BlueprintInfo::from_path("levels/World.glb"), // all we need is a Blueprint info...
        SpawnBlueprint, // and spawnblueprint to tell blenvy to spawn the blueprint now
        HideUntilReady, // only reveal the level once it is ready
        GameWorldTag,
    ));
}

// you can also spawn blueprint instances at runtime
pub fn spawn_blueprint_instance(keycode: Res<ButtonInput<KeyCode>>, mut commands: Commands) {
    if keycode.just_pressed(KeyCode::KeyS) {
        let mut rng = rand::rng();
        let range = 5.5;
        let x: f32 = rng.random_range(-range..range);
        let y: f32 = rng.random_range(-range..range);

        let mut rng = rand::rng();
        let range = 0.8;
        let vel_x: f32 = rng.random_range(-range..range);
        let vel_y: f32 = rng.random_range(2.0..2.5);
        let vel_z: f32 = rng.random_range(-range..range);

        let name_index: u64 = rng.random();

        let __new_entity = commands
            .spawn((
                BluePrintBundle {
                    blueprint: BlueprintInfo::from_path("blueprints/Health_Pickup.glb"),
                    ..Default::default()
                },
                Dynamic,
                bevy::prelude::Name::from(format!("test{}", name_index)),
                HideUntilReady,
                AddToGameWorld,
                Transform::from_xyz(x, 2.0, y),
                LinearVelocity(Vec3::new(vel_x, vel_y, vel_z)),
            ))
            .id();
        //         commands.entity(world).add_child(new_entity);
    }
}
