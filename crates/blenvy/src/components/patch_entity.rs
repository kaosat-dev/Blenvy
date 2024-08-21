use bevy::{
    log::{info, warn},
    prelude::Entity,
    reflect::Reflect,
};

use super::{fake_entity, reflect_ext};

pub fn patch_reflect_entity(reflect: &mut dyn Reflect) -> Option<Entity> {
    // We can put here either `fake_entity::Entity` or `bevy::ecs::entity::Entity`, but the latter would result in a false downcast.
    let maybe_fake = reflect
        .downcast_mut::<fake_entity::Entity>() // TODO: doesn't work yet, seems like it doesnt work when it's a dynamic type
        .map(|fake| fake.name.clone());

    info!("{}", reflect.reflect_type_ident().unwrap());

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
