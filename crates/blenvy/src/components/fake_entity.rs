pub(crate) struct Entity {
    pub name: Option<String>,
}

const _: () = {
    use bevy::reflect as bevy_reflect;

    #[allow(unused_mut)]
    impl bevy_reflect::GetTypeRegistration for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
        Option<String>: bevy_reflect::FromReflect
            + bevy_reflect::TypePath
            + bevy_reflect::__macro_exports::RegisterForReflection,
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
            registration
        }
        #[inline(never)]
        fn register_type_dependencies(registry: &mut bevy_reflect::TypeRegistry) {
            <Option<String> as bevy_reflect::__macro_exports::RegisterForReflection>::__register(
                registry,
            );
        }
    }
    impl bevy_reflect::Typed for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
        Option<String>: bevy_reflect::FromReflect
            + bevy_reflect::TypePath
            + bevy_reflect::__macro_exports::RegisterForReflection,
    {
        fn type_info() -> &'static bevy_reflect::TypeInfo {
            static CELL: bevy_reflect::utility::NonGenericTypeInfoCell =
                bevy_reflect::utility::NonGenericTypeInfoCell::new();
            CELL.get_or_set(|| {
                bevy_reflect::TypeInfo::Struct(
                    bevy_reflect::StructInfo::new::<bevy::ecs::entity::Entity>(&[
                        // TODO: changed here
                        bevy_reflect::NamedField::new::<Option<String>>("name")
                            .with_custom_attributes(
                                bevy_reflect::attributes::CustomAttributes::default(),
                            ),
                    ])
                    .with_custom_attributes(bevy_reflect::attributes::CustomAttributes::default()),
                )
            })
        }
    }
    impl bevy_reflect::TypePath for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
    {
        fn type_path() -> &'static str {
            "bevy_ecs::entity::Entity"
        }
        fn short_type_path() -> &'static str {
            "Entity"
        }
        fn type_ident() -> Option<&'static str> {
            ::core::option::Option::Some("Entity")
        }
        fn crate_name() -> Option<&'static str> {
            ::core::option::Option::Some("bevy_ecs::entity".split(':').next().unwrap())
        }
        fn module_path() -> Option<&'static str> {
            ::core::option::Option::Some("bevy_ecs::entity")
        }
    }
    impl bevy_reflect::Struct for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
        Option<String>: bevy_reflect::FromReflect
            + bevy_reflect::TypePath
            + bevy_reflect::__macro_exports::RegisterForReflection,
    {
        fn field(&self, name: &str) -> ::core::option::Option<&dyn bevy_reflect::Reflect> {
            match name {
                "name" => ::core::option::Option::Some(&self.name),
                _ => ::core::option::Option::None,
            }
        }
        fn field_mut(
            &mut self,
            name: &str,
        ) -> ::core::option::Option<&mut dyn bevy_reflect::Reflect> {
            match name {
                "name" => ::core::option::Option::Some(&mut self.name),
                _ => ::core::option::Option::None,
            }
        }
        fn field_at(&self, index: usize) -> ::core::option::Option<&dyn bevy_reflect::Reflect> {
            match index {
                0usize => ::core::option::Option::Some(&self.name),
                _ => ::core::option::Option::None,
            }
        }
        fn field_at_mut(
            &mut self,
            index: usize,
        ) -> ::core::option::Option<&mut dyn bevy_reflect::Reflect> {
            match index {
                0usize => ::core::option::Option::Some(&mut self.name),
                _ => ::core::option::Option::None,
            }
        }
        fn name_at(&self, index: usize) -> ::core::option::Option<&str> {
            match index {
                0usize => ::core::option::Option::Some("name"),
                _ => ::core::option::Option::None,
            }
        }
        fn field_len(&self) -> usize {
            1usize
        }
        fn iter_fields(&self) -> bevy_reflect::FieldIter {
            bevy_reflect::FieldIter::new(self)
        }
        fn clone_dynamic(&self) -> bevy_reflect::DynamicStruct {
            let mut dynamic: bevy_reflect::DynamicStruct = ::core::default::Default::default();
            dynamic.set_represented_type(bevy_reflect::Reflect::get_represented_type_info(self));
            dynamic.insert_boxed("name", bevy_reflect::Reflect::clone_value(&self.name));
            dynamic
        }
    }
    impl bevy_reflect::Reflect for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
        Option<String>: bevy_reflect::FromReflect
            + bevy_reflect::TypePath
            + bevy_reflect::__macro_exports::RegisterForReflection,
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
            ::std::boxed::Box::new(bevy_reflect::Struct::clone_dynamic(self))
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
        fn try_apply(
            &mut self,
            value: &dyn bevy_reflect::Reflect,
        ) -> ::core::result::Result<(), bevy_reflect::ApplyError> {
            if let bevy_reflect::ReflectRef::Struct(struct_value) =
                bevy_reflect::Reflect::reflect_ref(value)
            {
                for (i, value) in ::core::iter::Iterator::enumerate(
                    bevy_reflect::Struct::iter_fields(struct_value),
                ) {
                    let name = bevy_reflect::Struct::name_at(struct_value, i).unwrap();
                    if let ::core::option::Option::Some(v) =
                        bevy_reflect::Struct::field_mut(self, name)
                    {
                        bevy_reflect::Reflect::try_apply(v, value)?;
                    }
                }
            } else {
                return ::core::result::Result::Err(bevy_reflect::ApplyError::MismatchedKinds {
                    from_kind: bevy_reflect::Reflect::reflect_kind(value),
                    to_kind: bevy_reflect::ReflectKind::Struct,
                });
            }
            ::core::result::Result::Ok(())
        }
        #[inline]
        fn reflect_kind(&self) -> bevy_reflect::ReflectKind {
            bevy_reflect::ReflectKind::Struct
        }
        #[inline]
        fn reflect_ref(&self) -> bevy_reflect::ReflectRef {
            bevy_reflect::ReflectRef::Struct(self)
        }
        #[inline]
        fn reflect_mut(&mut self) -> bevy_reflect::ReflectMut {
            bevy_reflect::ReflectMut::Struct(self)
        }
        #[inline]
        fn reflect_owned(self: ::std::boxed::Box<Self>) -> bevy_reflect::ReflectOwned {
            bevy_reflect::ReflectOwned::Struct(self)
        }
        fn reflect_partial_eq(
            &self,
            value: &dyn bevy_reflect::Reflect,
        ) -> ::core::option::Option<bool> {
            bevy_reflect::struct_partial_eq(self, value)
        }
    }
    impl bevy_reflect::FromReflect for Entity
    where
        Self: ::core::any::Any + ::core::marker::Send + ::core::marker::Sync,
        Option<String>: bevy_reflect::FromReflect
            + bevy_reflect::TypePath
            + bevy_reflect::__macro_exports::RegisterForReflection,
    {
        fn from_reflect(reflect: &dyn bevy_reflect::Reflect) -> ::core::option::Option<Self> {
            if let bevy_reflect::ReflectRef::Struct(__ref_struct) =
                bevy_reflect::Reflect::reflect_ref(reflect)
            {
                ::core::option::Option::Some(Self {
                    name: (|| {
                        <Option<String> as bevy_reflect::FromReflect>::from_reflect(
                            bevy_reflect::Struct::field(__ref_struct, "name")?,
                        )
                    })()?,
                })
            } else {
                ::core::option::Option::None
            }
        }
    }
};
