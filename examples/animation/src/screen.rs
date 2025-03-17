use blenvy::{
    BlenvyPlugin, BlueprintAnimationPlayerLink, BlueprintAnimations, BlueprintInfo, GameWorldTag,
    HideUntilReady, SpawnBlueprint,
};
use std::time::Duration;

use bevy::{input::mouse::MouseMotion, prelude::*};

pub struct ScreenPlugin;
pub use crate::{Fox, Player, Robot};

// #[derive(Debug, Component)]
// struct MouseControlEnable(bool);

// #[derive(Component)]
// struct Screen;

// #[derive(Debug, Component)]
// struct ViewCarmera;

impl Plugin for ScreenPlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((BlenvyPlugin::default(),))
            .register_type::<Player>()
            .register_type::<Fox>()
            .register_type::<Robot>()
            .add_systems(
                Startup,
                (
                    spawn_world_model,
                    // spawn_view_model
                ),
            )
            .add_systems(
                Update,
                (
                    // move_camera,
                    animation_control, // text_input_listener.after(TextInputSystem),
                ),
            );
    }
}

fn spawn_world_model(mut commands: Commands) {
    commands.spawn((
        BlueprintInfo::from_path("levels/World.glb"), // all we need is a Blueprint info...
        SpawnBlueprint, // and spawnblueprint to tell blenvy to spawn the blueprint now
        HideUntilReady, // only reveal the level once it is ready
        GameWorldTag,
    ));
}

// fn spawn_view_model(
//     mut commands: Commands,
//     // mut meshes: ResMut<Assets<Mesh>>,
//     // mut materials: ResMut<Assets<StandardMaterial>>,
//     camera_query: Query<Entity, With<Camera>>,
// ) {
//     // Remove any existing cameras
//     for camera_entity in camera_query.iter() {
//         commands.entity(camera_entity).despawn();
//     }
//     // let arm = meshes.add(Cuboid::new(0.1, 0.1, 0.5));
//     // let arm_material = materials.add(Color::from(tailwind::TEAL_200));

//     // commands.spawn((
//     // 			TextInputBundle::default(),
//     // ));

//     commands
//         .spawn((
//             SpatialBundle {
//                 transform: Transform::from_xyz(0.0, 2.0, 0.0),
//                 ..default()
//             },
//             Screen,
//         ))
//         .with_children(|parent| {
//             parent.spawn((
//                 ViewCarmera,
//                 Camera3dBundle {
//                     transform: Transform::from_xyz(0.0, 10.0, 60.0).looking_at(Vec3::ZERO, Vec3::Y),
//                     camera: Camera {
//                         // Assign order 0 to the world model camera
//                         order: 0,
//                         ..default()
//                     },
//                     projection: PerspectiveProjection {
//                         fov: 20.0_f32.to_radians(),
//                         ..default()
//                     }
//                     .into(),
//                     ..default()
//                 },
//                 MouseControlEnable(true),
//             ));
//         });
// }

// fn move_camera(
//     time: Res<Time>,
//     mut mouse_motion: EventReader<MouseMotion>,
//     input: Res<ButtonInput<KeyCode>>,
//     mut world_model_projection: Query<&mut Transform, With<ViewCarmera>>,
//     mut mouse_control_query: Query<&mut MouseControlEnable>,
// ) {
//     let mut transform = world_model_projection.single_mut();
//     let mut mouse_control_enable = mouse_control_query.single_mut();

//     for motion in mouse_motion.read() {
//         if mouse_control_enable.0 {
//             let yaw = -motion.delta.x * 0.002;
//             let pitch = -motion.delta.y * 0.002;
//             // Order of rotations is important, see <https://gamedev.stackexchange.com/a/136175/103059>
//             transform.rotate_y(yaw);
//             transform.rotate_local_x(pitch);
//         }
//     }

//     let mut velocity = Vec3::ZERO;

//     let local_z = transform.local_z();
//     let forward = -Vec3::new(local_z.x, 0.0, local_z.z).normalize();
//     let right = Vec3::new(local_z.z, 0.0, -local_z.x).normalize();

//     let speed = 30.0;

//     for key in input.get_pressed() {
//         match key {
//             KeyCode::KeyW | KeyCode::ArrowUp => velocity += forward,
//             KeyCode::KeyS | KeyCode::ArrowDown => velocity -= forward,
//             KeyCode::KeyA | KeyCode::ArrowLeft => velocity -= right,
//             KeyCode::KeyD | KeyCode::ArrowRight => velocity += right,
//             KeyCode::KeyF => mouse_control_enable.0 = !mouse_control_enable.0,
//             KeyCode::Space => velocity += Vec3::Y,
//             KeyCode::ShiftLeft => velocity -= Vec3::Y,
//             _ => (),
//         }
//     }

//     velocity = velocity.normalize_or_zero();
//     transform.translation += velocity * speed * time.delta_seconds();
// }

pub fn animation_control(
    animated_robots: Query<(&BlueprintAnimationPlayerLink, &BlueprintAnimations), With<Robot>>,
    animated_foxes: Query<(&BlueprintAnimationPlayerLink, &BlueprintAnimations), With<Fox>>,

    mut animation_players: Query<(&mut AnimationPlayer, &mut AnimationTransitions)>,

    keycode: Res<ButtonInput<KeyCode>>,
    // mut entities_with_animations : Query<(&mut AnimationPlayer, &mut BlueprintAnimations)>,
) {
    // robots
    if keycode.just_pressed(KeyCode::KeyB) {
        println!("scan animation for robots");
        for (link, animations) in animated_robots.iter() {
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();
            println!("got some animations");
            let anim_name = "Scan";
            animation_transitions
                .play(
                    &mut animation_player,
                    *animations
                        .named_indices
                        .get(anim_name)
                        .expect("animation name should be in the list"),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    // foxes
    if keycode.just_pressed(KeyCode::KeyW) {
        for (link, animations) in animated_foxes.iter() {
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Walk";
            animation_transitions
                .play(
                    &mut animation_player,
                    *animations
                        .named_indices
                        .get(anim_name)
                        .expect("animation name should be in the list"),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyX) {
        println!("scan animation for fox - {:?}", animated_foxes);
        for (link, animations) in animated_foxes.iter() {
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Run";
            animation_transitions
                .play(
                    &mut animation_player,
                    *animations
                        .named_indices
                        .get(anim_name)
                        .expect("animation name should be in the list"),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    if keycode.just_pressed(KeyCode::KeyC) {
        for (link, animations) in animated_foxes.iter() {
            let (mut animation_player, mut animation_transitions) =
                animation_players.get_mut(link.0).unwrap();

            let anim_name = "Survey";
            animation_transitions
                .play(
                    &mut animation_player,
                    *animations
                        .named_indices
                        .get(anim_name)
                        .expect("animation name should be in the list"),
                    Duration::from_secs(5),
                )
                .repeat();
        }
    }

    /* Improveement ideas for the future
    // a bit more ideal API
    if keycode.just_pressed(KeyCode::B) {
        for (animation_player, animations) in  animated_robots.iter() {
            let anim_name = "Scan";
            if animations.named_animations.contains_key(anim_name) {
                let clip = animations.named_animations.get(anim_name).unwrap();
                animation_player.play_with_transition(clip.clone(), Duration::from_secs(5)).repeat();
            }
        }
    }

    // even better API
    if keycode.just_pressed(KeyCode::B) {
        for (animation_player, animations) in  animated_robots.iter() {
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
