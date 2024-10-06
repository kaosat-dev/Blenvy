use std::time::Duration;

/*use blenvy::{
    AnimationInfos, AnimationMarkerReached, BlueprintAnimationPlayerLink, BlueprintAnimations,
    InstanceAnimationPlayerLink, InstanceAnimations,
};*/

use bevy::prelude::*;

use blenvy::{
    AnimationInfos, AnimationMarkerReached, BlueprintAnimationPlayerLink, BlueprintAnimations,
    InstanceAnimationPlayerLink, InstanceAnimations,
};

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component for testing
pub struct Marker1;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component for testing
pub struct Marker2;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component for testing
pub struct Marker3;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component for testing; this is at the BLUEPRINT level
pub struct MarkerAllFoxes;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component for testing; this is at the INSTANCE level
pub struct MarkerSpecificFox;

/*
#[allow(clippy::type_complexity)]
pub fn animations(
    added_animation_players: Query<(Entity, &Name, &AnimationPlayer)>,
    added_animation_infos: Query<(Entity, &Name, &AnimationInfos), Added<AnimationInfos>>,
    animtest: Res<AnimTest>,
    mut commands: Commands,
    assets_gltf: Res<Assets<Gltf>>,
    parents: Query<&Parent>,
) {
    for (entity, name, animation_infos) in added_animation_infos.iter() {
        //debug!("animated stuf {:?} on entity {}", animation_infos, name);
        let gltf = assets_gltf.get(&animtest.0).unwrap();
        let mut matching_data = true;
        for animation_info in &animation_infos.animations {
            if !gltf.named_animations.contains_key(&animation_info.name) {
                matching_data = false;
                break;
            }
        }
        if matching_data {
            debug!(
                "inserting Animations components into {} ({:?})",
                name, entity
            );
            debug!("Found match {:?}", gltf.named_animations);
            commands.entity(entity).insert(InstanceAnimations {
                named_animations: gltf.named_animations.clone(),
            });
            for ancestor in parents.iter_ancestors(entity) {
                if added_animation_players.contains(ancestor) {
                    // debug!("found match with animationPlayer !! {:?}",names.get(ancestor));
                    commands
                        .entity(entity)
                        .insert(InstanceAnimationPlayerLink(ancestor));
                }
                // info!("{:?} is an ancestor of {:?}", ancestor, player);
            }
        }
    }
}*/

#[allow(clippy::type_complexity)]
pub fn play_animations(
    animated_foxes: Query<
        (&BlueprintAnimationPlayerLink, &BlueprintAnimations),
        With<MarkerAllFoxes>,
    >,
    animated_fox: Query<
        (&BlueprintAnimationPlayerLink, &BlueprintAnimations),
        With<MarkerSpecificFox>,
    >,

    animated_marker1: Query<
        (&InstanceAnimationPlayerLink, &InstanceAnimations),
        (With<AnimationInfos>, With<Marker1>),
    >,

    animated_marker2: Query<
        (&InstanceAnimationPlayerLink, &InstanceAnimations),
        (With<AnimationInfos>, With<Marker2>),
    >,

    with_blueprint_and_scene_animations: Query<
        (
            &InstanceAnimationPlayerLink,
            &InstanceAnimations,
            &BlueprintAnimationPlayerLink,
            &BlueprintAnimations,
        ),
        (With<AnimationInfos>, With<Marker3>),
    >,
    mut animation_players: Query<(&mut AnimationPlayer, &mut AnimationTransitions)>,
    keycode: Res<ButtonInput<KeyCode>>,
) {
    if keycode.just_pressed(KeyCode::KeyQ) {
        debug!("playing fox blueprint animation requested");
        for (link, animations) in animated_fox.iter() {
            debug!("BAR");

            // debug!("animations {:?}", animations.named_animations);
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();
            let anim_name = "Survey";
            let animation_index = *animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list");

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();

            /*let Some((&playing_animation_index, _)) = animation_player.playing_animations().next() else {
                continue;
            };
            let playing_animation = animation_player.animation_mut(playing_animation_index).unwrap();
            debug!("Playing animation {:?}", playing_animation);
            playing_animation.set_repeat(RepeatAnimation::Forever);*/
        }
    }

    if keycode.just_pressed(KeyCode::KeyP) {
        debug!("playing fox blueprint animation requested");
        for (link, animations) in animated_foxes.iter() {
            // debug!("animations {:?}", animations.named_animations);
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();
            let anim_name = "Run";
            let animation_index = *animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list");

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();

            /*let Some((&playing_animation_index, _)) = animation_player.playing_animations().next() else {
                continue;
            };
            let playing_animation = animation_player.animation_mut(playing_animation_index).unwrap();
            debug!("Playing animation {:?}", playing_animation);
            playing_animation.set_repeat(RepeatAnimation::Forever);*/
        }
        debug!(" ");
    }

    if keycode.just_pressed(KeyCode::KeyO) {
        debug!("playing marker 3 blueprint animation requested");
        for (_, _, link, animations) in with_blueprint_and_scene_animations.iter() {
            // This only works for entities that are spawned as part of the level, as scene animations are only there in that case
            // debug!("animations {:?}", animations.named_animations.keys());
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();
            let anim_name = "Walk";
            let animation_index = *animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list");

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyI) {
        debug!("playing marker 3 scene animation requested");
        for (link, animations, _, _) in with_blueprint_and_scene_animations.iter() {
            //debug!("animations {:?}", animations.named_animations.keys());
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint8_move";
            let animation_index = *animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list");

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyU) {
        for (link, animations) in animated_marker1.iter() {
            debug!("animations {:?}", animations.named_animations);
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Blueprint1_move";
            let animation_index = *animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list");

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
    if keycode.just_pressed(KeyCode::KeyY) {
        for (link, animations) in animated_marker1.iter() {
            debug!("animations {:?}", animations.named_animations);
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Blueprint1_jump";
            let animation_index = *animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list");

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
    if keycode.just_pressed(KeyCode::KeyT) {
        for (link, animations) in animated_marker2.iter() {
            debug!("animations {:?}", animations.named_animations);
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Blueprint1_move";
            let animation_index = *animations
                .named_indices
                .get(anim_name)
                .expect("animation name should be in the list");

            animation_transitions
                .play(
                    &mut animation_player,
                    animation_index,
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }
}

pub fn __react_to_animation_markers(
    mut animation_marker_events: EventReader<AnimationMarkerReached>,
) {
    for event in animation_marker_events.read() {
        debug!("animation marker event {:?}", event)
    }
}
