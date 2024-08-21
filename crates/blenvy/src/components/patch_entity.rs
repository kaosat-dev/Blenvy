use bevy::{
    log::{info, warn},
    prelude::Entity,
    reflect::{FromReflect, Reflect},
};

use super::{fake_entity, reflect_ext};

pub fn patch_reflect_entity(reflect: &mut dyn Reflect) -> Option<Entity> {
    let maybe_fake = fake_entity::Entity::from_reflect(reflect).map(|fake| fake.name.clone());

    if let Some(reference) = maybe_fake {
        let entity = if let Some(name) = reference {
            info!("Found name {name}");
            bevy::ecs::entity::Entity::PLACEHOLDER
        } else {
            warn!("No object was specified for Entity relation, using `Entity::PLACEHOLDER`.");
            bevy::ecs::entity::Entity::PLACEHOLDER
        };
        Some(entity)
    } else {
        let reflect_mut = reflect.reflect_mut();
        let iter = reflect_ext::DynamicFieldIterMut::from_reflect_mut(reflect_mut);
        // TODO: recursively update
        for f in iter {
            patch_reflect_entity(f);
        }
        None
    }
}
