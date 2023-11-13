pub mod in_game;
use bevy_gltf_blueprints::GameWorldTag;
pub use in_game::*;

pub mod in_main_menu;
pub use in_main_menu::*;

pub mod picking;
pub use picking::*;

use crate::{
    insert_dependant_component,
    state::{AppState, GameState, InAppRunning}, assets::GameAssets,
};
use bevy::prelude::*;
use bevy_rapier3d::prelude::*;

// this file is just for demo purposes, contains various types of components, systems etc

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub enum SoundMaterial {
    Metal,
    Wood,
    Rock,
    Cloth,
    Squishy,
    #[default]
    None,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Player;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo component showing auto injection of components
pub struct ShouldBeWithPlayer;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Interactible;

fn player_move_demo(
    keycode: Res<Input<KeyCode>>,
    mut players: Query<&mut Transform, With<Player>>,
) {
    let speed = 0.2;
    if let Ok(mut player) = players.get_single_mut() {
        if keycode.pressed(KeyCode::Left) {
            player.translation.x += speed;
        }
        if keycode.pressed(KeyCode::Right) {
            player.translation.x -= speed;
        }

        if keycode.pressed(KeyCode::Up) {
            player.translation.z += speed;
        }
        if keycode.pressed(KeyCode::Down) {
            player.translation.z -= speed;
        }
    }
}

// collision tests/debug
pub fn test_collision_events(
    mut collision_events: EventReader<CollisionEvent>,
    mut contact_force_events: EventReader<ContactForceEvent>,
) {
    for collision_event in collision_events.read() {
        println!("collision");
        match collision_event {
            CollisionEvent::Started(_entity1, _entity2, _) => {
                println!("collision started")
            }
            CollisionEvent::Stopped(_entity1, _entity2, _) => {
                println!("collision ended")
            }
        }
    }

    for contact_force_event in contact_force_events.read() {
        println!("Received contact force event: {:?}", contact_force_event);
    }
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct LevelTransition{
    pub target: String
}

pub fn trigger_level_transition(
    mut collision_events: EventReader<CollisionEvent>,
    level_transition_triggers: Query<&LevelTransition>,

    mut commands: Commands,
    game_assets: Res<GameAssets>,
    models: Res<Assets<bevy::gltf::Gltf>>,

    game_world: Query<(Entity, &GameWorldTag)>
){
    for collision_event in collision_events.read() {
        println!("collision");
        match collision_event {
            CollisionEvent::Started(entity1, entity2, _) => {
                if level_transition_triggers.get(*entity1).is_ok() ||  level_transition_triggers.get(*entity2).is_ok() {
                    println!("collision started, we can transition to level");
                    let transition_trigger;
                    if level_transition_triggers.get(*entity1).is_ok() {
                        transition_trigger = level_transition_triggers.get(*entity1).unwrap();
                    }else {
                        transition_trigger = level_transition_triggers.get(*entity2).unwrap();
                    }
                    let current_game_world = game_world.single();
                    // remove current level/world
                    commands.entity(current_game_world.0).despawn_recursive();

                    let target_level = &transition_trigger.target;
                    let level;
                    println!("target level {}", target_level);
                    if target_level == "Level1"{
                        level = &game_assets.level1;
                    }else {
                        level = &game_assets.world;
                    }

                    commands.spawn((
                        SceneBundle {
                            // note: because of this issue https://github.com/bevyengine/bevy/issues/10436, "world" is now a gltf file instead of a scene
                            scene: models
                                .get(level.id())
                                .expect("main level should have been loaded")
                                .scenes[0]
                                .clone(),
                            ..default()
                        },
                        bevy::prelude::Name::from("world"),
                        GameWorldTag,
                        InAppRunning,
                    ));

                }
            }
            CollisionEvent::Stopped(_entity1, _entity2, _) => {
                println!("collision ended")
            }
        }
    }
}

pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins(PickingPlugin)
            .register_type::<Interactible>()
            .register_type::<SoundMaterial>()
            .register_type::<Player>()

            .register_type::<LevelTransition>()

            // little helper utility, to automatically inject components that are dependant on an other component
            // ie, here an Entity with a Player component should also always have a ShouldBeWithPlayer component
            // you get a warning if you use this, as I consider this to be stop-gap solution (usually you should have either a bundle, or directly define all needed components)
            .add_systems(
                Update,
                (
                    // insert_dependant_component::<Player, ShouldBeWithPlayer>,
                    player_move_demo, //.run_if(in_state(AppState::Running)),
                    test_collision_events,
                    spawn_test,
                    trigger_level_transition,
                )
                    .run_if(in_state(GameState::InGame)),
            )
            .add_systems(OnEnter(AppState::MenuRunning), setup_main_menu)
            .add_systems(OnExit(AppState::MenuRunning), teardown_main_menu)
            .add_systems(Update, (main_menu))
            .add_systems(OnEnter(AppState::AppRunning), setup_game);
    }
}
