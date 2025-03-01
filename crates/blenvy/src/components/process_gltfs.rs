use std::ops::Deref;

use bevy::{
    core::Name,
    ecs::{
        entity::Entity,
        query::{Added, Without},
        reflect::{AppTypeRegistry, ReflectComponent},
        system::{SystemParam, SystemState},
        world::World,
    },
    gltf::{GltfExtras, GltfMaterialExtras, GltfMeshExtras, GltfSceneExtras},
    hierarchy::Parent,
    log::{debug, warn},
    prelude::{HierarchyQueryExt, Local, Query, Res},
    reflect::{Reflect, TypeRegistration},
    scene::SceneInstance,
    utils::HashMap,
};

use crate::{ronstring_to_reflect_component, GltfProcessed};

use super::fake_entity::{self, BadWorldAccess};

// , mut entity_components: HashMap<Entity, Vec<(Box<dyn Reflect>, TypeRegistration)>>
fn find_entity_components(
    entity: Entity,
    name: Option<&Name>,
    parent: Option<&Parent>,
    reflect_components: Vec<(Box<dyn Reflect>, TypeRegistration)>,
    entity_components: &HashMap<Entity, Vec<(Box<dyn Reflect>, TypeRegistration)>>,
) -> (Entity, Vec<(Box<dyn Reflect>, TypeRegistration)>) {
    // we assign the components specified /xxx_components objects to their parent node
    let mut target_entity = entity;
    // if the node contains "components" or ends with "_pa" (ie add to parent), the components will not be added to the entity itself but to its parent
    // this is mostly used for Blender collections
    if parent.is_some() {
        if let Some(name) = name {
            if name.as_str().contains("components") || name.as_str().ends_with("_pa") {
                debug!("adding components to parent");
                target_entity = parent.expect("the target entity had a parent ").get();
            }
        }
    }
    debug!("adding to {:?}", target_entity);

    // if there where already components set to be added to this entity (for example when entity_data was refering to a parent), update the vec of entity_components accordingly
    // this allows for example blender collection to provide basic ecs data & the instances to override/ define their own values
    if entity_components.contains_key(&target_entity) {
        let mut updated_components: Vec<(Box<dyn Reflect>, TypeRegistration)> = Vec::new();
        let current_components = &entity_components[&target_entity];
        // first inject the current components
        for (component, type_registration) in current_components {
            updated_components.push((component.clone_value(), type_registration.clone()));
        }
        // then inject the new components: this also enables overwrite components set in the collection
        for (component, type_registration) in reflect_components {
            updated_components.push((component.clone_value(), type_registration));
        }
        return (target_entity, updated_components);
    }
    (target_entity, reflect_components)
}

#[derive(SystemParam)]
#[doc(hidden)]
pub struct ExtrasComponentQueries<'w, 's> {
    extras: Query<
        'w,
        's,
        (Entity, Option<&'static Name>, &'static GltfExtras),
        (Added<GltfExtras>, Without<GltfProcessed>),
    >,
    scene_extras: Query<
        'w,
        's,
        (Entity, Option<&'static Name>, &'static GltfSceneExtras),
        (Added<GltfSceneExtras>, Without<GltfProcessed>),
    >,
    mesh_extras: Query<
        'w,
        's,
        (Entity, Option<&'static Name>, &'static GltfMeshExtras),
        (Added<GltfMeshExtras>, Without<GltfProcessed>),
    >,
    material_extras: Query<
        'w,
        's,
        (Entity, Option<&'static Name>, &'static GltfMaterialExtras),
        (Added<GltfMaterialExtras>, Without<GltfProcessed>),
    >,
    // Hierarchy and Scene instances are both here and in BadWorldAccess, but they don't clash because read-only.
    bad_world_access: BadWorldAccess<'w, 's>,
    hierarchy: Query<'w, 's, &'static Parent>,
    scene_instances: Query<'w, 's, &'static SceneInstance>,
    type_registry: Res<'w, AppTypeRegistry>,
}

/// main function: injects components into each entity in gltf files that have `gltf_extras`, using reflection
pub fn add_components_from_gltf_extras(
    world: &mut World,
    mut queries_state: Local<Option<SystemState<ExtrasComponentQueries<'_, '_>>>>,
) {
    let state = queries_state.get_or_insert_with(|| SystemState::new(world));
    let ExtrasComponentQueries {
        extras,
        scene_extras,
        mesh_extras,
        material_extras,
        bad_world_access,
        hierarchy,
        scene_instances,
        type_registry,
    } = state.get_mut(world);

    let mut entity_components: HashMap<Entity, Vec<(Box<dyn Reflect>, TypeRegistration)>> =
        HashMap::new();

    // let gltf_components_config = world.resource::<GltfComponentsConfig>();

    unsafe {
        // SAFETY: we set this to `None` again before using world again and fake_entity just uses it in that time.
        fake_entity::BAD_WORLD_ACCESS.set(Some(core::mem::transmute(bad_world_access)));
    }

    for (entity, name, extra) in extras.iter() {
        let parent = hierarchy.get(entity).ok();
        debug!(
            "Gltf Extra: Name: {:?}, entity {:?}, parent: {:?}, extras {:?}",
            name, entity, parent, extra
        );

        if let Some(instance) = hierarchy
            .iter_ancestors(entity)
            .find_map(|p| scene_instances.get(p).ok())
        {
            fake_entity::INSTANCE_ID.set(Some(*instance.deref()));
        } else {
            warn!("Can't find higher-hierarchy `SceneInstance` for entity '{name:?}'");
            fake_entity::INSTANCE_ID.set(None);
        };

        let mut type_registry = type_registry.write();
        let reflect_components = ronstring_to_reflect_component(&extra.value, &mut type_registry);
        // let name = name.unwrap_or(&Name::new(""));

        let (target_entity, updated_components) =
            find_entity_components(entity, name, parent, reflect_components, &entity_components);

        entity_components.insert(target_entity, updated_components);
    }

    for (entity, name, extra) in scene_extras.iter() {
        let parent = hierarchy.get(entity).ok();
        debug!(
            "Gltf Scene Extra: Name: {:?}, entity {:?}, parent: {:?}, scene_extras {:?}",
            name, entity, parent, extra
        );

        if let Some(instance) = hierarchy
            .iter_ancestors(entity)
            .find_map(|p| scene_instances.get(p).ok())
        {
            fake_entity::INSTANCE_ID.set(Some(*instance.deref()));
        } else {
            warn!("Can't find higher-hierarchy `SceneInstance` for entity '{name:?}'");
            fake_entity::INSTANCE_ID.set(None);
        };

        let mut type_registry = type_registry.write();
        let reflect_components = ronstring_to_reflect_component(&extra.value, &mut type_registry);

        let (target_entity, updated_components) =
            find_entity_components(entity, name, parent, reflect_components, &entity_components);
        entity_components.insert(target_entity, updated_components);
    }

    for (entity, name, extra) in mesh_extras.iter() {
        let parent = hierarchy.get(entity).ok();
        debug!(
            "Gltf Mesh Extra: Name: {:?}, entity {:?}, parent: {:?}, mesh_extras {:?}",
            name, entity, parent, extra
        );

        if let Some(instance) = hierarchy
            .iter_ancestors(entity)
            .find_map(|p| scene_instances.get(p).ok())
        {
            fake_entity::INSTANCE_ID.set(Some(*instance.deref()));
        } else {
            warn!("Can't find higher-hierarchy `SceneInstance` for entity '{name:?}'");
            fake_entity::INSTANCE_ID.set(None);
        };

        let mut type_registry = type_registry.write();
        let reflect_components = ronstring_to_reflect_component(&extra.value, &mut type_registry);

        let (target_entity, updated_components) =
            find_entity_components(entity, name, parent, reflect_components, &entity_components);
        entity_components.insert(target_entity, updated_components);
    }

    for (entity, name, extra) in material_extras.iter() {
        let parent = hierarchy.get(entity).ok();
        debug!(
            "Name: {:?}, entity {:?}, parent: {:?}, material_extras {:?}",
            name, entity, parent, extra
        );

        if let Some(instance) = hierarchy
            .iter_ancestors(entity)
            .find_map(|p| scene_instances.get(p).ok())
        {
            fake_entity::INSTANCE_ID.set(Some(*instance.deref()));
        } else {
            warn!("Can't find higher-hierarchy `SceneInstance` for entity '{name:?}'");
            fake_entity::INSTANCE_ID.set(None);
        };

        let mut type_registry = type_registry.write();
        let reflect_components = ronstring_to_reflect_component(&extra.value, &mut type_registry);

        let (target_entity, updated_components) =
            find_entity_components(entity, name, parent, reflect_components, &entity_components);
        entity_components.insert(target_entity, updated_components);
    }

    fake_entity::BAD_WORLD_ACCESS.set(None);
    fake_entity::INSTANCE_ID.set(None);

    for (entity, components) in entity_components {
        let type_registry: &AppTypeRegistry = world.resource();
        let type_registry = type_registry.clone();
        let type_registry = type_registry.read();

        if !components.is_empty() {
            debug!("--entity {:?}, components {}", entity, components.len());
        }
        for (component, type_registration) in components {
            debug!(
                "------adding {} {:?}",
                component.get_represented_type_info().unwrap().type_path(),
                component
            );

            {
                let mut entity_mut = world.entity_mut(entity);
                let Some(reflected_component) = type_registration.data::<ReflectComponent>() else {
                    warn!(?component, "unable to reflect component");
                    entity_mut.insert(GltfProcessed);
                    continue;
                };
                reflected_component.insert(&mut entity_mut, &*component, &type_registry);

                entity_mut.insert(GltfProcessed); //
            }
        }
    }
}
