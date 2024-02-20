use bevy::{
    core::Name,
    ecs::{
        entity::Entity,
        query::Added,
        reflect::{AppTypeRegistry, ReflectComponent},
        world::World,
    },
    gltf::GltfExtras,
    hierarchy::Parent,
    log::debug,
    reflect::{Reflect, TypeRegistration},
    utils::HashMap,
};

use crate::{ronstring_to_reflect_component, GltfComponentsConfig};

/// main function: injects components into each entity in gltf files that have `gltf_extras`, using reflection
pub fn add_components_from_gltf_extras(world: &mut World) {
    let mut extras =
        world.query_filtered::<(Entity, &Name, &GltfExtras, &Parent), Added<GltfExtras>>();
    let mut entity_components: HashMap<Entity, Vec<(Box<dyn Reflect>, TypeRegistration)>> =
        HashMap::new();

    let gltf_components_config = world.resource::<GltfComponentsConfig>();

    for (entity, name, extra, parent) in extras.iter(world) {
        debug!(
            "Name: {}, entity {:?}, parent: {:?}, extras {:?}",
            name, entity, parent, extra
        );

        let type_registry: &AppTypeRegistry = world.resource();
        let type_registry = type_registry.read();
            
        let reflect_components = ronstring_to_reflect_component(
            &extra.value,
            &type_registry,
            gltf_components_config.legacy_mode,
        );

        // we assign the components specified /xxx_components objects to their parent node
        let mut target_entity = entity;
        // if the node contains "components" or ends with "_pa" (ie add to parent), the components will not be added to the entity itself but to its parent
        // this is mostly used for Blender collections
        if name.as_str().contains("components") || name.as_str().ends_with("_pa") {
            debug!("adding components to parent");
            target_entity = parent.get();
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
            entity_components.insert(target_entity, updated_components);
        } else {
            entity_components.insert(target_entity, reflect_components);
        }
    }

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
                type_registration
                .data::<ReflectComponent>()
                .expect("Unable to reflect component")
                .insert(&mut entity_mut, &*component, &type_registry); // TODO: how can we insert any additional components "by hand" here ?
            }
        }
    }
}
