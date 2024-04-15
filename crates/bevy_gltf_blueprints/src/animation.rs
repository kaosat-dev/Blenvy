use bevy::prelude::*;
use bevy::utils::HashMap;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// storage for animations for a given entity's BLUEPRINT (ie for example a characters animations), essentially a clone of gltf's `named_animations`
pub struct BlueprintAnimations {
    pub named_animations: HashMap<String, Handle<AnimationClip>>,
}

#[derive(Component, Debug)]
/// Stop gap helper component : this is inserted into a "root" entity (an entity representing a whole gltf file)
/// so that the root entity knows which of its children contains an actualy `AnimationPlayer` component
/// this is for convenience, because currently , Bevy's gltf parsing inserts `AnimationPlayers` "one level down"
/// ie armature/root for animated models, which means more complex queries to trigger animations that we want to avoid
pub struct BlueprintAnimationPlayerLink(pub Entity);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// storage for scene level animations for a given entity (hierarchy), essentially a clone of gltf's `named_animations`
pub struct SceneAnimations {
    pub named_animations: HashMap<String, Handle<AnimationClip>>,
}

#[derive(Component, Debug)]
/// Stop gap helper component : this is inserted into a "root" entity (an entity representing a whole gltf file)
/// so that the root entity knows which of its children contains an actualy `AnimationPlayer` component
/// this is for convenience, because currently , Bevy's gltf parsing inserts `AnimationPlayers` "one level down"
/// ie armature/root for animated models, which means more complex queries to trigger animations that we want to avoid
pub struct SceneAnimationPlayerLink(pub Entity);

/// Stores Animation information: name, frame informations etc
#[derive(Reflect, Default, Debug)]
pub struct AnimationInfo {
    pub name: String,
    pub frame_start: f32,
    pub frame_end: f32,
    pub frames_length: f32,
    pub frame_start_override: f32,
    pub frame_end_override: f32,
}

/// Stores information about animations, to make things a bit easier api wise:
/// these components are automatically inserted by `gltf_auto_export` on entities that have animations
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct AnimationInfos {
    pub animations: Vec<AnimationInfo>,
}

#[derive(Reflect, Default, Debug)]
pub struct AnimationMarker {
    // pub frame: u32,
    pub name: String,
    pub handled_for_cycle: bool,
}

/// Stores information about animation markers: practical for adding things like triggering events at specific keyframes etc
/// it is essentiall a hashmap of `AnimationName` => `HashMap`<`FrameNumber`, Vec of marker names>
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct AnimationMarkers(pub HashMap<String, HashMap<u32, Vec<String>>>);

/// Event that gets triggered once a specific marker inside an animation has been reached (frame based)
/// Provides some usefull information about which entity , wich animation, wich frame & which marker got triggered
#[derive(Event, Debug)]
pub struct AnimationMarkerReached {
    pub entity: Entity,
    pub animation_name: String,
    pub frame: u32,
    pub marker_name: String,
}

/////////////////////

/// triggers events when a given animation marker is reached for INSTANCE animations
pub fn trigger_instance_animation_markers_events(
    animation_infos: Query<(
        Entity,
        &AnimationMarkers,
        &SceneAnimationPlayerLink,
        &SceneAnimations,
        &AnimationInfos,
    )>,
    animation_players: Query<&AnimationPlayer>,
    animation_clips: Res<Assets<AnimationClip>>,
    mut animation_marker_events: EventWriter<AnimationMarkerReached>,
) {
    for (entity, markers, link, animations, animation_infos) in animation_infos.iter() {
        let animation_player = animation_players.get(link.0).unwrap();
        let animation_clip = animation_clips.get(animation_player.animation_clip());

        if animation_clip.is_some() {
            // println!("Entity {:?} markers {:?}", entity, markers);
            // println!("Player {:?} {}", animation_player.elapsed(), animation_player.completions());
            // FIMXE: yikes ! very inneficient ! perhaps add boilerplate to the "start playing animation" code so we know what is playing
            let animation_name = animations.named_animations.iter().find_map(|(key, value)| {
                if value == animation_player.animation_clip() {
                    Some(key)
                } else {
                    None
                }
            });
            if animation_name.is_some() {
                let animation_name = animation_name.unwrap();

                let animation_length_seconds = animation_clip.unwrap().duration();
                let animation_length_frames = animation_infos
                    .animations
                    .iter()
                    .find(|anim| &anim.name == animation_name)
                    .unwrap()
                    .frames_length;
                // TODO: we also need to take playback speed into account
                let time_in_animation = animation_player.elapsed()
                    - (animation_player.completions() as f32) * animation_length_seconds;
                let frame_seconds =
                    (animation_length_frames / animation_length_seconds) * time_in_animation;
                let frame = frame_seconds as u32;

                let matching_animation_marker = &markers.0[animation_name];
                if matching_animation_marker.contains_key(&frame) {
                    let matching_markers_per_frame = matching_animation_marker.get(&frame).unwrap();

                    // let timediff = animation_length_seconds - time_in_animation;
                    // println!("timediff {}", timediff);
                    // println!("FOUND A MARKER {:?} at frame {}", matching_markers_per_frame, frame);
                    // emit an event AnimationMarkerReached(entity, animation_name, frame, marker_name)
                    // FIXME: problem, this can fire multiple times in a row, depending on animation length , speed , etc
                    for marker in matching_markers_per_frame {
                        animation_marker_events.send(AnimationMarkerReached {
                            entity,
                            animation_name: animation_name.clone(),
                            frame,
                            marker_name: marker.clone(),
                        });
                    }
                }
            }
        }
    }
}

/// triggers events when a given animation marker is reached for BLUEPRINT animations
pub fn trigger_blueprint_animation_markers_events(
    animation_infos: Query<(Entity, &BlueprintAnimationPlayerLink, &BlueprintAnimations)>,
    // FIXME: annoying hiearchy issue yet again: the Markers & AnimationInfos are stored INSIDE the blueprint, so we need to access them differently
    all_animation_infos: Query<(Entity, &AnimationMarkers, &AnimationInfos, &Parent)>,
    animation_players: Query<&AnimationPlayer>,
    animation_clips: Res<Assets<AnimationClip>>,
    mut animation_marker_events: EventWriter<AnimationMarkerReached>,
) {
    for (entity, link, animations) in animation_infos.iter() {
        let animation_player = animation_players.get(link.0).unwrap();
        let animation_clip = animation_clips.get(animation_player.animation_clip());

        // FIXME: horrible code
        for (_, markers, animation_infos, parent) in all_animation_infos.iter() {
            if parent.get() == entity {
                if animation_clip.is_some() {
                    // println!("Entity {:?} markers {:?}", entity, markers);
                    // println!("Player {:?} {}", animation_player.elapsed(), animation_player.completions());
                    // FIMXE: yikes ! very inneficient ! perhaps add boilerplate to the "start playing animation" code so we know what is playing
                    let animation_name =
                        animations.named_animations.iter().find_map(|(key, value)| {
                            if value == animation_player.animation_clip() {
                                Some(key)
                            } else {
                                None
                            }
                        });
                    if animation_name.is_some() {
                        let animation_name = animation_name.unwrap();
                        let animation_length_seconds = animation_clip.unwrap().duration();
                        let animation_length_frames = animation_infos
                            .animations
                            .iter()
                            .find(|anim| &anim.name == animation_name)
                            .unwrap()
                            .frames_length;
                        // TODO: we also need to take playback speed into account
                        let time_in_animation = animation_player.elapsed()
                            - (animation_player.completions() as f32) * animation_length_seconds;
                        let frame_seconds = (animation_length_frames / animation_length_seconds)
                            * time_in_animation;
                        // println!("frame seconds {}", frame_seconds);
                        let frame = frame_seconds.ceil() as u32; // FIXME , bad hack

                        let matching_animation_marker = &markers.0[animation_name];

                        if matching_animation_marker.contains_key(&frame) {
                            let matching_markers_per_frame =
                                matching_animation_marker.get(&frame).unwrap();
                            // println!("FOUND A MARKER {:?} at frame {}", matching_markers_per_frame, frame);
                            // emit an event AnimationMarkerReached(entity, animation_name, frame, marker_name)
                            // FIXME: complete hack-ish solution , otherwise this can fire multiple times in a row, depending on animation length , speed , etc
                            let diff = frame as f32 - frame_seconds;
                            println!("diff {}", diff);
                            if diff < 0.1 {
                                for marker in matching_markers_per_frame {
                                    animation_marker_events.send(AnimationMarkerReached {
                                        entity,
                                        animation_name: animation_name.clone(),
                                        frame,
                                        marker_name: marker.clone(),
                                    });
                                }
                            }
                        }
                    }
                }

                break;
            }
        }
    }
}
