use bevy::prelude::*;
use bevy::utils::HashMap;

// FIXME: move to more relevant module
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct Animations {
    pub named_animations: HashMap<String, Handle<AnimationClip>>,
}

#[derive(Component, Debug)]
pub struct AnimationPlayerLink(pub Entity);


#[derive(Reflect)]
struct PlayingAnimation {
    repeat: bool,
    speed: f32,
    elapsed: f32,
    animation_clip: Handle<AnimationClip>,
    path_cache: Vec<Vec<Option<Entity>>>,
}

impl Default for PlayingAnimation {
    fn default() -> Self {
        Self {
            repeat: false,
            speed: 1.0,
            elapsed: 0.0,
            animation_clip: Default::default(),
            path_cache: Vec::new(),
        }
    }
}

/// An animation that is being faded out as part of a transition
struct AnimationTransition {
    /// The current weight. Starts at 1.0 and goes to 0.0 during the fade-out.
    current_weight: f32,
    /// How much to decrease `current_weight` per second
    weight_decline_per_sec: f32,
    /// The animation that is being faded out
    animation: PlayingAnimation,
}

/// Animation controls
#[derive(Component, Default, Reflect)]
#[reflect(Component)]
pub struct AnimationController {
    paused: bool,

    animation: PlayingAnimation,

    // List of previous animations we're currently transitioning away from.
    // Usually this is empty, when transitioning between animations, there is
    // one entry. When another animation transition happens while a transition
    // is still ongoing, then there can be more than one entry.
    // Once a transition is finished, it will be automatically removed from the list
    #[reflect(ignore)]
    transitions: Vec<AnimationTransition>,

    pub animations: Animations

}