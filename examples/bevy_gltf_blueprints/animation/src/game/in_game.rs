use bevy_gltf_worlflow_examples_common_rapier::{
    assets::GameAssets, GameState, InAppRunning, Player,
};
use bevy_rapier3d::prelude::Velocity;
use rand::Rng;
use std::time::Duration;

use bevy::prelude::*;

use bevy_gltf_blueprints::{
    BlueprintAnimationPlayerLink, BlueprintAnimations, BluePrintBundle, BlueprintName, GameWorldTag,
};

use super::{Fox, Robot};

pub fn setup_game(
    mut commands: Commands,
    game_assets: Res<GameAssets>,
    models: Res<Assets<bevy::gltf::Gltf>>,

    mut next_game_state: ResMut<NextState<GameState>>,
) {
    commands.insert_resource(AmbientLight {
        color: Color::WHITE,
        brightness: 0.2,
    });
    // here we actually spawn our game world/level

    commands.spawn((
        SceneBundle {
            // note: because of this issue https://github.com/bevyengine/bevy/issues/10436, "world" is now a gltf file instead of a scene
            scene: models
                .get(game_assets.world.clone().unwrap().id())
                .expect("main level should have been loaded")
                .scenes[0]
                .clone(),
            ..default()
        },
        bevy::prelude::Name::from("world"),
        GameWorldTag,
        InAppRunning,
    ));

    next_game_state.set(GameState::InGame)
}

pub fn spawn_test(
    keycode: Res<ButtonInput<KeyCode>>,
    mut commands: Commands,

    mut game_world: Query<(Entity, &Children), With<GameWorldTag>>,
) {
    if keycode.just_pressed(KeyCode::KeyT) {
        let world = game_world.single_mut();
        let world = world.1[0];

        let mut rng = rand::thread_rng();
        let range = 8.5;
        let x: f32 = rng.gen_range(-range..range);
        let y: f32 = rng.gen_range(-range..range);

        let mut rng = rand::thread_rng();
        let range = 0.8;
        let vel_x: f32 = rng.gen_range(-range..range);
        let vel_y: f32 = rng.gen_range(2.0..2.5);
        let vel_z: f32 = rng.gen_range(-range..range);

        let name_index: u64 = rng.gen();

        let new_entity = commands
            .spawn((
                BluePrintBundle {
                    blueprint: BlueprintName("Fox".to_string()),
                    ..Default::default()
                },
                bevy::prelude::Name::from(format!("Spawned{}", name_index)),
                // BlueprintName("Health_Pickup".to_string()),
                // SpawnHere,
                TransformBundle::from_transform(Transform::from_xyz(x, 0.0, y)),
                Velocity {
                    linvel: Vec3::new(vel_x, vel_y, vel_z),
                    angvel: Vec3::new(0.0, 0.0, 0.0),
                },
            ))
            .id();
        commands.entity(world).add_child(new_entity);
    }
}

// example of changing animation of entities based on proximity to the player, for "fox" entities (Tag component)
pub fn animation_change_on_proximity_foxes(
    players: Query<&GlobalTransform, With<Player>>,
    animated_foxes: Query<(&GlobalTransform, &BlueprintAnimationPlayerLink, &BlueprintAnimations), With<Fox>>,

    mut animation_players: Query<&mut AnimationPlayer>,
) {
    for player_transforms in players.iter() {
        for (fox_tranforms, link, animations) in animated_foxes.iter() {
            let distance = player_transforms
                .translation()
                .distance(fox_tranforms.translation());
            let mut anim_name = "Walk";
            if distance < 8.5 {
                anim_name = "Run";
            } else if (8.5..10.0).contains(&distance) {
                anim_name = "Walk";
            } else if (10.0..15.0).contains(&distance) {
                anim_name = "Survey";
            }
            // now play the animation based on the chosen animation name
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(3),
                )
                .repeat();
        }
    }
}

// example of changing animation of entities based on proximity to the player, this time for the "robot" entities  (Tag component)
pub fn animation_change_on_proximity_robots(
    players: Query<&GlobalTransform, With<Player>>,
    animated_robots: Query<(&GlobalTransform, &BlueprintAnimationPlayerLink, &BlueprintAnimations), With<Robot>>,

    mut animation_players: Query<&mut AnimationPlayer>,
) {
    for player_transforms in players.iter() {
        for (robot_tranforms, link, animations) in animated_robots.iter() {
            let distance = player_transforms
                .translation()
                .distance(robot_tranforms.translation());

            let mut anim_name = "Idle";
            if distance < 8.5 {
                anim_name = "Jump";
            } else if (8.5..10.0).contains(&distance) {
                anim_name = "Scan";
            } else if (10.0..15.0).contains(&distance) {
                anim_name = "Idle";
            }

            // now play the animation based on the chosen animation name
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(3),
                )
                .repeat();
        }
    }
}

pub fn animation_control(
    animated_enemies: Query<(&BlueprintAnimationPlayerLink, &BlueprintAnimations), With<Robot>>,
    animated_foxes: Query<(&BlueprintAnimationPlayerLink, &BlueprintAnimations), With<Fox>>,

    mut animation_players: Query<&mut AnimationPlayer>,

    keycode: Res<ButtonInput<KeyCode>>,
    // mut entities_with_animations : Query<(&mut AnimationPlayer, &mut BlueprintAnimations)>,
) {
    // robots
    if keycode.just_pressed(KeyCode::KeyB) {
        for (link, animations) in animated_enemies.iter() {
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Scan";
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    // foxes
    if keycode.just_pressed(KeyCode::KeyW) {
        for (link, animations) in animated_foxes.iter() {
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Walk";
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyX) {
        for (link, animations) in animated_foxes.iter() {
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Run";
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyC) {
        for (link, animations) in animated_foxes.iter() {
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Survey";
            animation_player
                .play_with_transition(
                    animations
                        .named_animations
                        .get(anim_name)
                        .expect("animation name should be in the list")
                        .clone(),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    /* Improveement ideas for the future
    // a bit more ideal API
    if keycode.just_pressed(KeyCode::B) {
        for (animation_player, animations) in  animated_enemies.iter() {
            let anim_name = "Scan";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                animation_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
    }

    // even better API
    if keycode.just_pressed(KeyCode::B) {
        for (animation_player, animations) in  animated_enemies.iter() {
            animation_player.play_with_transition("Scan", Duration::from_secs(5)).repeat(); // with a merged animationPlayer + animations storage
            // alternative, perhaps more realistic, and better seperation of concerns
            animation_player.play_with_transition(animations, "Scan", Duration::from_secs(5)).repeat();

        }
    }*/

    /*for (mut anim_player, animations) in entities_with_animations.iter_mut(){

        if keycode.just_pressed(KeyCode::W) {
            let anim_name = "Walk";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                anim_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
        if keycode.just_pressed(KeyCode::X) {
            let anim_name = "Run";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                anim_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
        if keycode.just_pressed(KeyCode::C) {
            let anim_name = "Survey";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                anim_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }



        if keycode.just_pressed(KeyCode::S) {
            let anim_name = "Scan";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                anim_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
        if keycode.just_pressed(KeyCode::I) {
            let anim_name = "Idle";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                anim_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
    }*/
}
