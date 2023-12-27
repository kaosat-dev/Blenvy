use bevy::ecs::system::Command;
use bevy::prelude::*;

// modified version from https://github.com/bevyengine/bevy/issues/1515,
// more specifically https://gist.github.com/nwtnni/85d6b87ae75337a522166c500c9a8418
// to work with Bevy 0.11
pub struct CloneEntity {
    pub source: Entity,
    pub destination: Entity,
}

impl CloneEntity {
    // Copy all components from an entity to another.
    // Using an entity with no components as the destination creates a copy of the source entity.
    // Panics if:
    // - the components are not registered in the type registry,
    // - the world does not have a type registry
    // - the source or destination entity do not exist
    fn clone_entity(self, world: &mut World) {
        let components = {
            let registry = world
                .get_resource::<AppTypeRegistry>()
                .expect("the world should have a type registry")
                .read();

            world
                .get_entity(self.source)
                .expect("source entity should exist")
                .archetype()
                .components()
                .map(|component_id| {
                    let component_info = world
                        .components()
                        .get_info(component_id)
                        .expect("component info should be available");

                    let type_id = component_info.type_id().unwrap();
                    let type_id = registry.get(type_id).expect(
                        format!(
                            "cannot clone entity: component: {:?} is not registered",
                            component_info.name()
                        )
                        .as_str(),
                    );
                    return type_id.data::<ReflectComponent>().unwrap().clone();
                })
                .collect::<Vec<_>>()
        };

        for component in components {
            let source = component
                .reflect(world.get_entity(self.source).unwrap())
                .unwrap()
                .clone_value();

            let mut destination = world
                .get_entity_mut(self.destination)
                .expect("destination entity should exist");

            component.apply_or_insert(&mut destination, &*source);
        }
    }
}

// This allows the command to be used in systems
impl Command for CloneEntity {
    fn apply(self, world: &mut World) {
        self.clone_entity(world)
    }
}
