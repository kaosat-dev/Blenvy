
## SystemSet

the ordering of systems is very important ! 

For example to replace your proxy components (stand-in components when you cannot/ do not want to use real components in the gltf file) with actual ones, which should happen **AFTER** the Blueprint based spawning, 

so ```blenvy``` provides a **SystemSet** for that purpose: ```GltfBlueprintsSet```

Typically , the order of systems should be

***blenvy (GltfComponentsSet::Injection)*** => ***blenvy (GltfBlueprintsSet::Spawn, GltfBlueprintsSet::AfterSpawn)*** => ***replace_proxies***

see https://github.com/kaosat-dev/Blenvy/tree/main/examples/blenvy/basic for how to set it up correctly



## Animation

```blenvy``` provides some lightweight helpers to deal with animations stored in gltf files

 * an ```Animations``` component that gets inserted into spawned (root) entities that contains a hashmap of all animations contained inside that entity/gltf file .
 (this is a copy of the ```named_animations``` inside Bevy's gltf structures )
 * an ```AnimationPlayerLink``` component that gets inserted into spawned (root) entities, to make it easier to trigger/ control animations than it usually is inside Bevy + Gltf files

The workflow for animations is as follows:
* create a gltf file with animations (using Blender & co) as you would normally do
* inside Bevy, use the ```blenvy``` boilerplate (see sections above), no specific setup beyond that is required
* to control the animation of an entity, you need to query for entities that have both ```AnimationPlayerLink``` and ```Animations``` components (added by ```blenvy```) AND entities with the ```AnimationPlayer``` component
 
For example:

```rust no_run
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
```

see https://github.com/kaosat-dev/Blenvy/tree/main/examples/blenvy/animation for how to set it up correctly

