use bevy::prelude::*;
use bevy::scene::SceneInstance;
use bevy::utils::hashbrown::HashSet;

use crate::{InBlueprint, OriginalChildren};

use super::{AnimationPlayerLink, Animations};
use super::{CloneEntity, SpawnHere};
use super::{SpawnedRoot};

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
    unprocessed_entities: Query<
        (Entity, &Children, Option<&Name>, &OriginalChildren, &Animations),
        (With<SpawnHere>, With<SpawnedRoot>, With<SceneInstance>, Without<SpawnedRootProcessed>),
    >,
    added_animation_players: Query<(Entity, &Parent), Added<AnimationPlayer>>,
    all_children: Query<&Children>,

    mut commands: Commands,

) {

    for (original, children, name, original_children, animations) in unprocessed_entities.iter() {
        info!("this ones needs work {:?}", name);
       
        if children.len() == 0 {
            warn!("timing issue ! no children found, please restart your bevy app (bug being investigated)");
            continue;
        }
        // the root node is the first & normally only child inside a scene, it is the one that has all relevant components
        let mut root_entity = Entity::PLACEHOLDER;//FIXME: and what about childless ones ?? => should not be possible normally
        // let diff = HashSet::from_iter(original_children.0).difference(HashSet::from_iter(children));
        // we find the first child that was not in the entity before (aka added during the scene spawning)
        for c in children.iter(){
            if !original_children.0.contains(c){
                root_entity = *c;
                break;
            }
        }
      
        // we flag all children of the blueprint instance with 'InBlueprint'
        // can be usefull to filter out anything that came from blueprints vs normal children   
        for child in all_children.iter_descendants(root_entity) {
            commands.entity(child).insert(InBlueprint);
        }

        // transfer data into from blueprint instance's root_entity to original entity
        commands.add(CloneEntity {
            source: root_entity ,
            destination: original
        });

        // we move all of children of the blueprint instance one level to the original entity
        if let Ok(root_entity_children) = all_children.get(root_entity) {
            for child in root_entity_children.iter(){
                // info!("copying child {:?} upward from {:?} to {:?}", names.get(*child), root_entity, original);
                commands.entity(original).add_child(*child);
            }
        }

        if animations.named_animations.keys().len() > 0 {
            for (added, parent) in added_animation_players.iter() {
                if parent.get() == root_entity {
                    // FIXME: stopgap solution: since we cannot use an AnimationPlayer at the root entity level
                    // and we cannot update animation clips so that the EntityPaths point to one level deeper,
                    // BUT we still want to have some marker/control at the root entity level, we add this
                    commands
                        .entity(original)
                        .insert(AnimationPlayerLink(added));
                }
            }
        }

        info!("cleanup {:?}", name);
        commands.entity(original).remove::<SpawnHere>();
        commands.entity(original).remove::<Handle<Scene>>();
        commands.entity(root_entity).despawn_recursive();
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
