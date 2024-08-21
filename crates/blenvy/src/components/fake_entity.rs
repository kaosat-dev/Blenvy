use std::{alloc::Layout, num::NonZeroU32};

use bevy::{
    log::{info, warn},
    reflect::ReflectDeserialize,
};
use serde::Deserialize;

const _: () = {
    let real = Layout::new::<bevy::ecs::entity::Entity>();
    let fake = Layout::new::<Entity>();
    assert!(real.size() == fake.size());
    assert!(real.align() == fake.align());
};

#[derive(Clone)]
#[repr(C, align(8))]
pub(crate) struct Entity {
    // Do not reorder the fields here. The ordering is equivalent to bevy's `Entity`
    #[cfg(target_endian = "little")]
    index: u32,
    generation: NonZeroU32,
    #[cfg(target_endian = "big")]
    index: u32,
}

impl<'de> Deserialize<'de> for Entity {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        #[derive(Deserialize)]
        #[serde(rename = "Entity")]
        struct EntityData {
            name: Option<String>,
        }

        let entity_data = EntityData::deserialize(deserializer)?;

        let entity = if let Some(name) = entity_data.name {
            info!("Found name {name}");
            bevy::ecs::entity::Entity::PLACEHOLDER
        } else {
            warn!("No object was specified for Entity relation, using `Entity::PLACEHOLDER`.");
            bevy::ecs::entity::Entity::PLACEHOLDER
        };

        Ok(unsafe {
            // SAFETY: both have the same layout
            core::mem::transmute(entity)
        })
    }
}

// This is expanded and modified from
// ```
// #[derive(Clone, Reflect)]
// #[reflect_value(Deserialize)]
// ```
const _: () = {
    use bevy::reflect as bevy_reflect;

    #[allow(unused_mut)]
    impl bevy_reflect::GetTypeRegistration for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
    {
        fn get_type_registration() -> bevy_reflect::TypeRegistration {
            let mut registration = bevy_reflect::TypeRegistration::of::<Self>();
            registration
                .insert::<
                    bevy_reflect::ReflectFromPtr,
                >(bevy_reflect::FromType::<Self>::from_type());
            registration.insert::<bevy_reflect::ReflectFromReflect>(
                bevy_reflect::FromType::<Self>::from_type(),
            );
            registration.insert::<ReflectDeserialize>(bevy_reflect::FromType::<Self>::from_type());
            registration
        }
    }
    impl bevy_reflect::TypePath for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
    {
        fn type_path() -> &'static str {
            "bevy_ecs::entity::Entity" // this is changed
        }
        fn short_type_path() -> &'static str {
            "Entity"
        }
        fn type_ident() -> Option<&'static str> {
            ::core::option::Option::Some("Entity")
        }
        fn crate_name() -> Option<&'static str> {
            // this is changed
            ::core::option::Option::Some("bevy_ecs::entity".split(':').next().unwrap())
        }
        fn module_path() -> Option<&'static str> {
            ::core::option::Option::Some("bevy_ecs::entity") // this is changed
        }
    }
    impl bevy_reflect::Typed for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
    {
        fn type_info() -> &'static bevy_reflect::TypeInfo {
            static CELL: bevy_reflect::utility::NonGenericTypeInfoCell =
                bevy_reflect::utility::NonGenericTypeInfoCell::new();
            CELL.get_or_set(|| {
                let info = bevy_reflect::ValueInfo::new::<bevy::ecs::entity::Entity>(); // this is changed
                bevy_reflect::TypeInfo::Value(info)
            })
        }
    }
    impl bevy_reflect::Reflect for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
    {
        #[inline]
        fn get_represented_type_info(
            &self,
        ) -> ::core::option::Option<&'static bevy_reflect::TypeInfo> {
            ::core::option::Option::Some(<Self as bevy_reflect::Typed>::type_info())
        }
        #[inline]
        fn into_any(self: ::std::boxed::Box<Self>) -> ::std::boxed::Box<dyn ::core::any::Any> {
            self
        }
        #[inline]
        fn as_any(&self) -> &dyn ::core::any::Any {
            self
        }
        #[inline]
        fn as_any_mut(&mut self) -> &mut dyn ::core::any::Any {
            self
        }
        #[inline]
        fn into_reflect(
            self: ::std::boxed::Box<Self>,
        ) -> ::std::boxed::Box<dyn bevy_reflect::Reflect> {
            self
        }
        #[inline]
        fn as_reflect(&self) -> &dyn bevy_reflect::Reflect {
            self
        }
        #[inline]
        fn as_reflect_mut(&mut self) -> &mut dyn bevy_reflect::Reflect {
            self
        }
        #[inline]
        fn clone_value(&self) -> ::std::boxed::Box<dyn bevy_reflect::Reflect> {
            ::std::boxed::Box::new(::core::clone::Clone::clone(self))
        }
        #[inline]
        fn try_apply(
            &mut self,
            value: &dyn bevy_reflect::Reflect,
        ) -> ::core::result::Result<(), bevy_reflect::ApplyError> {
            let any = bevy_reflect::Reflect::as_any(value);
            if let ::core::option::Option::Some(value) =
                <dyn ::core::any::Any>::downcast_ref::<Self>(any)
            {
                *self = ::core::clone::Clone::clone(value);
            } else {
                return ::core::result::Result::Err(bevy_reflect::ApplyError::MismatchedTypes {
                    from_type: ::core::convert::Into::into(
                        bevy_reflect::DynamicTypePath::reflect_type_path(value),
                    ),
                    to_type: ::core::convert::Into::into(
                        <Self as bevy_reflect::TypePath>::type_path(),
                    ),
                });
            }
            ::core::result::Result::Ok(())
        }
        #[inline]
        fn set(
            &mut self,
            value: ::std::boxed::Box<dyn bevy_reflect::Reflect>,
        ) -> ::core::result::Result<(), ::std::boxed::Box<dyn bevy_reflect::Reflect>> {
            *self = <dyn bevy_reflect::Reflect>::take(value)?;
            ::core::result::Result::Ok(())
        }
        #[inline]
        fn reflect_kind(&self) -> bevy_reflect::ReflectKind {
            bevy_reflect::ReflectKind::Value
        }
        #[inline]
        fn reflect_ref(&self) -> bevy_reflect::ReflectRef {
            bevy_reflect::ReflectRef::Value(self)
        }
        #[inline]
        fn reflect_mut(&mut self) -> bevy_reflect::ReflectMut {
            bevy_reflect::ReflectMut::Value(self)
        }
        #[inline]
        fn reflect_owned(self: ::std::boxed::Box<Self>) -> bevy_reflect::ReflectOwned {
            bevy_reflect::ReflectOwned::Value(self)
        }
    }
    impl bevy_reflect::FromReflect for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
    {
        fn from_reflect(reflect: &dyn bevy_reflect::Reflect) -> ::core::option::Option<Self> {
            ::core::option::Option::Some(::core::clone::Clone::clone(
                <dyn ::core::any::Any>::downcast_ref::<Entity>(
                    <dyn bevy_reflect::Reflect>::as_any(reflect),
                )?,
            ))
        }
    }
};
