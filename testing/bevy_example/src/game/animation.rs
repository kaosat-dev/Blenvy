use std::time::Duration;

use bevy_gltf_blueprints::{
    AnimationInfos, AnimationMarkerReached, BlueprintAnimationPlayerLink, BlueprintAnimations,
    SceneAnimationPlayerLink, SceneAnimations,
};

use bevy::{gltf::Gltf, prelude::*};

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
/// flag component for testing
pub struct MarkerFox;

#[derive(Resource)]
pub struct AnimTest(Handle<Gltf>);

pub fn setup_main_scene_animations(asset_server: Res<AssetServer>, mut commands: Commands) {
    commands.insert_resource(AnimTest(asset_server.load("models/World.glb")));
}

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
        //println!("animated stuf {:?} on entity {}", animation_infos, name);
        let gltf = assets_gltf.get(&animtest.0).unwrap();
        let mut matching_data = true;
        for animation_info in &animation_infos.animations {
            if !gltf.named_animations.contains_key(&animation_info.name) {
                matching_data = false;
                break;
            }
        }
        if matching_data {
            println!(
                "inserting Animations components into {} ({:?})",
                name, entity
            );
            println!("Found match {:?}", gltf.named_animations);
            commands.entity(entity).insert(SceneAnimations {
                named_animations: gltf.named_animations.clone(),
            });
            for ancestor in parents.iter_ancestors(entity) {
                if added_animation_players.contains(ancestor) {
                    // println!("found match with animationPlayer !! {:?}",names.get(ancestor));
                    commands
                        .entity(entity)
                        .insert(SceneAnimationPlayerLink(ancestor));
                }
                // info!("{:?} is an ancestor of {:?}", ancestor, player);
            }
        }
    }
}

#[allow(clippy::type_complexity)]
pub fn play_animations(
    animated_marker1: Query<
        (&SceneAnimationPlayerLink, &SceneAnimations),
        (With<AnimationInfos>, With<Marker1>),
    >,
    animated_marker2: Query<
        (&SceneAnimationPlayerLink, &SceneAnimations),
        (With<AnimationInfos>, With<Marker2>),
    >,
    animated_marker3: Query<
        (
            &SceneAnimationPlayerLink,
            &SceneAnimations,
            &BlueprintAnimationPlayerLink,
            &BlueprintAnimations,
        ),
        (With<AnimationInfos>, With<Marker3>),
    >,

    animated_fox: Query<(&BlueprintAnimationPlayerLink, &BlueprintAnimations), With<MarkerFox>>,

    mut animation_players: Query<&mut AnimationPlayer>,
    keycode: Res<ButtonInput<KeyCode>>,
) {
    if keycode.just_pressed(KeyCode::KeyP) {
        for (link, animations) in animated_fox.iter() {
            println!("animations {:?}", animations.named_animations);
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

    if keycode.just_pressed(KeyCode::KeyM) {
        for (link, animations) in animated_marker1.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint1_move";
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
    if keycode.just_pressed(KeyCode::KeyJ) {
        for (link, animations) in animated_marker1.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint1_jump";
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

    if keycode.just_pressed(KeyCode::KeyA) {
        for (link, animations) in animated_marker2.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint1_move";
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
    if keycode.just_pressed(KeyCode::KeyB) {
        for (link, animations) in animated_marker2.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint1_jump";
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

    // play instance animation
    if keycode.just_pressed(KeyCode::KeyW) {
        for (link, animations, _, _) in animated_marker3.iter() {
            println!("animations {:?}", animations.named_animations);
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            let anim_name = "Blueprint8_move";
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
    // play blueprint animation
    if keycode.just_pressed(KeyCode::KeyX) {
        for (_, _, link, animations) in animated_marker3.iter() {
            println!("animations {:?}", animations.named_animations);
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
}

pub fn react_to_animation_markers(
    mut animation_marker_events: EventReader<AnimationMarkerReached>,
) {
    for event in animation_marker_events.read() {
        println!("animation marker event {:?}", event)
    }
}
