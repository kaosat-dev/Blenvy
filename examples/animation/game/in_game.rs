use std::time::Duration;

use bevy::prelude::*;

use crate::{
    assets::GameAssets,
    state::{GameState, InAppRunning},
};
use bevy_gltf_blueprints::{GameWorldTag, Animations, AnimationPlayerLink};

use super::{Enemy, Fox, Player};

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


pub fn animation_change_on_proximity(
    players: Query<&GlobalTransform, With<Player>>,
    animated_foxes: Query<(&GlobalTransform, &AnimationPlayerLink, &Animations ), With<Fox>>,

    mut animation_players: Query<&mut AnimationPlayer>,

){
    for player_transforms in players.iter() {
        for (fox_tranforms, link, animations) in animated_foxes.iter() {
            let distance = player_transforms
                .translation()
                .distance(fox_tranforms.translation());
            if distance < 8.5 {
                // commands.entity(pickable).despawn_recursive();
                let mut animation_player = animation_players.get_mut(link.0).unwrap();
                let anim_name = "Walk";
                animation_player.play_with_transition(
                    animations.named_animations.get(anim_name).expect("animation name should be in the list").clone(), 
                    Duration::from_secs(3)
                ).repeat();
            }
            else {
                let mut animation_player = animation_players.get_mut(link.0).unwrap();
                let anim_name = "Survey";
                animation_player.play_with_transition(
                    animations.named_animations.get(anim_name).expect("animation name should be in the list").clone(), 
                    Duration::from_secs(3)
                ).repeat();
            }
        }
    }
}

pub fn animation_control(
    animated_enemies: Query<(&AnimationPlayerLink, &Animations), With<Enemy>>,
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

    /*if keycode.just_pressed(KeyCode::B) {
        for (link, animations) in  animated_enemies.iter() {
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Scan";
            animation_player.play_with_transition(
                animations.named_animations.get(anim_name).expect("animation name should be in the list").clone(), Duration::from_secs(5)
            ).repeat();
            
        }
    }*/

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
            // alternative, perhaps more realistic
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