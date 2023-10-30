use std::time::Duration;

use bevy::prelude::*;

use crate::{
    assets::GameAssets,
    state::{GameState, InAppRunning},
};
use bevy_gltf_blueprints::{GameWorldTag, Animations, AnimationPlayerLink};

use super::Enemy;

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


pub fn animation_control(
    // mut entities_with_animations : Query<(&mut AnimationPlayer, &mut Animations)>,

    animated_enemies: Query<(&AnimationPlayerLink, &Animations), With<Enemy>>,
    mut animation_players: Query<&mut AnimationPlayer>,

    keycode: Res<Input<KeyCode>>,
) {
    if keycode.just_pressed(KeyCode::B) {
        for (link, animations) in  animated_enemies.iter() {
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Scan";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                animation_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
    }

    /* 
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
            animation_player.play_with_transition("Scan", Duration::from_secs(5)).repeat();
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