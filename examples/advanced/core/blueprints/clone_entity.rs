use bevy::prelude::*;
use bevy::ecs::system::Command;

// modified version from https://github.com/bevyengine/bevy/issues/1515,
// more specifically https://gist.github.com/nwtnni/85d6b87ae75337a522166c500c9a8418
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
          let registry = world.get_resource::<AppTypeRegistry>().unwrap().read();

          world
              .get_entity(self.source)
              .unwrap()
              .archetype()
              .components()
              .map(|component_id| {
                  world
                      .components()
                      .get_info(component_id)
                      .unwrap()
                      .type_id()
                      .unwrap()
              })
              .map(|type_id| {
                // println!("type_id {:?}", type_id);
                  registry
                      .get(type_id)
                      .unwrap()
                      .data::<ReflectComponent>()
                      .unwrap()
                      .clone()
              })
              .collect::<Vec<_>>()
      };

      for component in components {
          let source = component
              .reflect(world.get_entity(self.source).unwrap())
              .unwrap()
              .clone_value();

          let mut destination = world.get_entity_mut(self.destination).unwrap();

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