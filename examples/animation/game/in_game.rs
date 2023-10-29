use std::time::Duration;

use bevy::prelude::*;

use crate::{
    assets::GameAssets,
    state::{GameState, InAppRunning},
};
use bevy_gltf_blueprints::{GameWorldTag, Animations};

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
    mut entities_with_animations : Query<(&mut AnimationPlayer, &mut Animations)>,
    keycode: Res<Input<KeyCode>>,
) {
    for (mut anim_player, animations) in entities_with_animations.iter_mut(){

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
    }
}