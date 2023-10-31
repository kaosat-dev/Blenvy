use std::time::Duration;

use bevy::prelude::*;

use crate::{
    assets::GameAssets,
    state::{GameState, InAppRunning},
};
use bevy_gltf_blueprints::{GameWorldTag, Animations, AnimationPlayerLink};

use super::{Robot, Fox, Player};

pub fn setup_game(
    mut commands: Commands,
    game_assets: Res<GameAssets>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    println!("setting up all stuff");
    commands.insert_resource(AmbientLight {
        color: Color::WHITE,
        brightness: 0.2,
    });
    // here we actually spawn our game world/level

    commands.spawn((
        SceneBundle {
            scene: game_assets.world.clone(),
            ..default()
        },
        bevy::prelude::Name::from("world"),
        GameWorldTag,
        InAppRunning,
    ));

    next_game_state.set(GameState::InGame)
}

// example of changing animation of entities based on proximity to the player, for "fox" entities (Tag component)
pub fn animation_change_on_proximity_foxes(
    players: Query<&GlobalTransform, With<Player>>,
    animated_foxes: Query<(&GlobalTransform, &AnimationPlayerLink, &Animations ), With<Fox>>,

    mut animation_players: Query<&mut AnimationPlayer>,

){
    for player_transforms in players.iter() {
        for (fox_tranforms, link, animations) in animated_foxes.iter() {
            let distance = player_transforms
                .translation()
                .distance(fox_tranforms.translation());
            let mut anim_name = "Walk"; 
            if distance < 8.5 {
                anim_name = "Run"; 
            }
            else if distance >= 8.5 && distance < 10.0{
                anim_name = "Walk";
            }
            else if distance >= 10.0 && distance < 15.0{
                anim_name = "Survey";
            }
            // now play the animation based on the chosen animation name
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            animation_player.play_with_transition(
                animations.named_animations.get(anim_name).expect("animation name should be in the list").clone(), 
                Duration::from_secs(3)
            ).repeat();
        }
    }
}

// example of changing animation of entities based on proximity to the player, this time for the "robot" entities  (Tag component)
pub fn animation_change_on_proximity_robots(
    players: Query<&GlobalTransform, With<Player>>,
    animated_robots: Query<(&GlobalTransform, &AnimationPlayerLink, &Animations ), With<Robot>>,

    mut animation_players: Query<&mut AnimationPlayer>,

){
    for player_transforms in players.iter() {
        for (robot_tranforms, link, animations) in animated_robots.iter() {
            let distance = player_transforms
                .translation()
                .distance(robot_tranforms.translation());

            let mut anim_name = "Idle"; 
            if distance < 8.5 {
                anim_name = "Jump"; 
            }
            else if distance >= 8.5 && distance < 10.0{
                anim_name = "Scan";
            }
            else if distance >= 10.0 && distance < 15.0{
                anim_name = "Idle";
            }

            // now play the animation based on the chosen animation name
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            animation_player.play_with_transition(
                animations.named_animations.get(anim_name).expect("animation name should be in the list").clone(), 
                Duration::from_secs(3)
            ).repeat();

        }
    }
}


pub fn animation_control(
    animated_enemies: Query<(&AnimationPlayerLink, &Animations), With<Robot>>,
    animated_foxes: Query<(&AnimationPlayerLink, &Animations), With<Fox>>,

    mut animation_players: Query<&mut AnimationPlayer>,

    keycode: Res<Input<KeyCode>>,
    // mut entities_with_animations : Query<(&mut AnimationPlayer, &mut Animations)>,
) {
    // robots
    if keycode.just_pressed(KeyCode::B) {
        for (link, animations) in  animated_enemies.iter() {
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Scan";
            animation_player.play_with_transition(
                animations.named_animations.get(anim_name).expect("animation name should be in the list").clone(), 
                Duration::from_secs(5)
            ).repeat();
            
        }
    }

    // foxes
    if keycode.just_pressed(KeyCode::W) {
        for (link, animations) in  animated_foxes.iter() {
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Walk";
            animation_player.play_with_transition(
                animations.named_animations.get(anim_name).expect("animation name should be in the list").clone(), 
                Duration::from_secs(5)
            ).repeat();
        }
    }

     if keycode.just_pressed(KeyCode::X) {
        for (link, animations) in  animated_foxes.iter() {
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Run";
            animation_player.play_with_transition(
                animations.named_animations.get(anim_name).expect("animation name should be in the list").clone(), 
                Duration::from_secs(5)
            ).repeat();
        }
    }

    if keycode.just_pressed(KeyCode::C) {
        for (link, animations) in  animated_foxes.iter() {
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Survey";
            animation_player.play_with_transition(
                animations.named_animations.get(anim_name).expect("animation name should be in the list").clone(), 
                Duration::from_secs(5)
            ).repeat();
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