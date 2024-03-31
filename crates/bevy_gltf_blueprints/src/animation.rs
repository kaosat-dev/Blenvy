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
/// storage for animations for a given entity (hierarchy), essentially a clone of gltf's `named_animations`
pub struct InstanceAnimations {
    pub named_animations: HashMap<String, Handle<AnimationClip>>,
}

#[derive(Component, Debug)]
/// Stop gap helper component : this is inserted into a "root" entity (an entity representing a whole gltf file)
/// so that the root entity knows which of its children contains an actualy `AnimationPlayer` component
/// this is for convenience, because currently , Bevy's gltf parsing inserts `AnimationPlayers` "one level down"
/// ie armature/root for animated models, which means more complex queries to trigger animations that we want to avoid
pub struct InstanceAnimationPlayerLink(pub Entity);

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
/// these components are automatically inserted by gltf_auto_export on entities that have animations
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct AnimationInfos {
    pub animations: Vec<AnimationInfo>,
}

pub struct AnimationMarker {
    pub frame: u32,
    pub name: String,
}

/// Stores information about animation markers: practical for adding things like triggering events at specific keyframes etc
/// it is essentiall a hashmap of AnimationName => HashMap<FrameNumber, Vec of marker names>
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct AnimationMarkers(pub HashMap<String, HashMap<u32, Vec<String>>>);

// FIXME: ugh, ugly, there has to be a better way to do this ?
#[derive(Component, Default, Debug)]
pub struct AnimationMarkerTrackers(pub HashMap<String, HashMap<u32, Vec<AnimationMarkerTracker>>>);

#[derive(Default, Debug)]
pub struct AnimationMarkerTracker {
    // pub frame:u32,
    // pub name: String,
    // pub processed_for_cycle: bool,
    pub prev_frame: u32,
}

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
        &InstanceAnimationPlayerLink,
        &InstanceAnimations,
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
                    (animation_length_frames as f32 / animation_length_seconds) * time_in_animation;
                let frame = frame_seconds as u32;

                let matching_animation_marker = &markers.0[animation_name];
                if matching_animation_marker.contains_key(&frame) {
                    let matching_markers_per_frame = matching_animation_marker.get(&frame).unwrap();
                    // println!("FOUND A MARKER {:?} at frame {}", matching_markers_per_frame, frame);
                    // emit an event AnimationMarkerReached(entity, animation_name, frame, marker_name)
                    // FIXME: problem, this can fire multiple times in a row, depending on animation length , speed , etc
                    for marker_name in matching_markers_per_frame {
                        animation_marker_events.send(AnimationMarkerReached {
                            entity: entity,
                            animation_name: animation_name.clone(),
                            frame: frame,
                            marker_name: marker_name.clone(),
                        });
                    }
                }
            }
        }
    }
}

/// triggers events when a given animation marker is reached for BLUEPRINT animations
pub fn trigger_blueprint_animation_markers_events(
    animation_infos: Query<(
        Entity,
        &BlueprintAnimationPlayerLink,
        &BlueprintAnimations,
    )>,
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
        let mut markers:Option<&AnimationMarkers>= None;
        let mut animation_infos:Option<&AnimationInfos>=None;
        for (_, _markers, _animation_infos, parent) in all_animation_infos.iter(){
            if parent.get() == entity {
                markers = Some(_markers);
                animation_infos = Some(_animation_infos);
                break;
            }
        }
        if animation_clip.is_some() && markers.is_some() && animation_infos.is_some()  {
            let markers = markers.unwrap();
            let animation_infos = animation_infos.unwrap();

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
                    (animation_length_frames as f32 / animation_length_seconds) * time_in_animation;
                let frame = frame_seconds as u32;

                let matching_animation_marker = &markers.0[animation_name];
                if matching_animation_marker.contains_key(&frame) {
                    let matching_markers_per_frame = matching_animation_marker.get(&frame).unwrap();
                    // println!("FOUND A MARKER {:?} at frame {}", matching_markers_per_frame, frame);
                    // emit an event AnimationMarkerReached(entity, animation_name, frame, marker_name)
                    // FIXME: problem, this can fire multiple times in a row, depending on animation length , speed , etc
                    for marker_name in matching_markers_per_frame {
                        animation_marker_events.send(AnimationMarkerReached {
                            entity: entity,
                            animation_name: animation_name.clone(),
                            frame: frame,
                            marker_name: marker_name.clone(),
                        });
                    }
                }
            }
        }
    }
}