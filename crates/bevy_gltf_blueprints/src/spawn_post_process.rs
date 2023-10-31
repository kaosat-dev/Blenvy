use bevy::prelude::*;

use super::{CloneEntity, SpawnHere};
use super::{Original, SpawnedRoot};
use super::{Animations, AnimationPlayerLink};


#[derive(Component)]
/// FlagComponent for dynamically spawned scenes
pub(crate) struct SpawnedRootProcessed;

/// this system updates the first (and normally only) child of a scene flaged SpawnedRoot
/// - adds a name based on parent component (spawned scene) which is named on the scene name/prefab to be instanciated
// FIXME: updating hierarchy does not work in all cases ! this is sadly dependant on the structure of the exported blend data
// - blender root-> object with properties => WORKS
// - scene instance -> does not work
// it might be due to how we add components to the PARENT item in gltf to components
pub(crate) fn update_spawned_root_first_child(
    // 
    unprocessed_entities: Query<
        (Entity, &Children, &Name, &Parent, &Original),
        (With<SpawnedRoot>, Without<SpawnedRootProcessed>),
    >,
    mut commands: Commands,

    // FIXME: not sure , but might be better if done at a more generic gltf level 
    animations: Query<&Animations>,
    added_animation_players: Query<(Entity, &Parent), Added<AnimationPlayer>>,
) {
    /*
      currently we have
      - scene instance
          - root node ?
              - the actual stuff
      we want to remove the root node
      so we wend up with
      - scene instance
          - the actual stuff

      so
          - get root node
          - add its children to the scene instance
          - remove root node

      Another issue is, the scene instance become empty if we have a pickabke as the "actual stuff", so that would lead to a lot of
          empty scenes if we spawn pickables
      - perhaps another system that cleans up empty scene instances ?

      FIME: this is all highly dependent on the hierachy ;..
    */

    for (scene_instance, children, name, parent, original) in unprocessed_entities.iter() {
        //
        if children.len() == 0 {
            warn!("timing issue ! no children found, please restart your bevy app (bug being investigated)");
            // println!("children of scene {:?}", children);
            continue;
        }
        // the root node is the first & normally only child inside a scene, it is the one that has all relevant components
        let root_entity = children.first().unwrap(); //FIXME: and what about childless ones ?? => should not be possible normally
                                                     // let root_entity_data = all_children.get(*root_entity).unwrap();

        // fixme : randomization should be controlled via parameters, perhaps even the seed could be specified ?
        // use this https://rust-random.github.io/book/guide-seeding.html#a-simple-number, blenders seeds are also uInts
        // also this is not something we want every time, this should be a settable parameter when requesting a spawn

        // add missing name of entity, based on the wrapper's name
        let name = name.clone().replace("scene_wrapper_", "");

        // this is our new actual entity
        commands.entity(*root_entity).insert((
            bevy::prelude::Name::from(name.clone()),
            // ItemType {name},
        ));

        // flag the spawned_root as being processed
        commands.entity(scene_instance).insert(SpawnedRootProcessed);

        // parent is either the world or an entity with a marker (BlueprintName)
        commands.entity(parent.get()).add_child(*root_entity);
      
        
        let matching_animations = animations.get(scene_instance);

        if let Ok(animations) = matching_animations {
            if animations.named_animations.keys().len() > 0 {

            for (added, parent) in added_animation_players.iter() {
                if parent.get() == *root_entity {
                    // FIXME: stopgap solution: since we cannot use an AnimationPlayer at the root entity level
                    // and we cannot update animation clips so that the EntityPaths point to one level deeper,
                    // BUT we still want to have some marker/control at the root entity level, we add this
                    commands.entity(*root_entity).insert(AnimationPlayerLink(added));
                    commands.entity(*root_entity).insert(Animations {
                        named_animations: animations.named_animations.clone(),
                    });
                 }
            }
            }
        }
      
        commands.add(CloneEntity {
            source: original.0,
            destination: *root_entity,
        });

        // remove the original entity, now that we have cloned it into the spawned scenes first child
        commands.entity(original.0).despawn_recursive();
        commands.entity(*root_entity).remove::<SpawnHere>();
    }
}

/// cleans up dynamically spawned scenes so that they get despawned if they have no more children
pub(crate) fn cleanup_scene_instances(
    scene_instances: Query<(Entity, &Children), With<SpawnedRootProcessed>>,
    without_children: Query<Entity, (With<SpawnedRootProcessed>, Without<Children>)>, // if there are not children left, bevy removes Children ?
    mut commands: Commands,
) {
    for (entity, children) in scene_instances.iter() {
        if children.len() == 0 {
            // it seems this does not happen ?
            debug!("cleaning up emptied spawned scene instance");
            commands.entity(entity).despawn_recursive();
        }
    }
    for entity in without_children.iter() {
        debug!("cleaning up emptied spawned scene instance");
        commands.entity(entity).despawn_recursive();
    }
}
