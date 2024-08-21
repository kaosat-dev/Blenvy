use bevy::reflect::{Reflect, ReflectMut};

pub mod array_ext;
pub mod enum_ext;
pub mod list_ext;
pub mod map_ext;
pub mod struct_ext;
pub mod tuple_ext;
pub mod tuple_struct_ext;

pub enum DynamicFieldIterMut<'a> {
    Struct(struct_ext::FieldIterMut<'a>),
    TupleStruct(tuple_struct_ext::TupleStructFieldIterMut<'a>),
    Tuple(tuple_ext::TupleFieldIterMut<'a>),
    List(list_ext::ListIterMut<'a>),
    Array(array_ext::ArrayIterMut<'a>),
    Map(map_ext::MapIterMut<'a>),
    Enum(enum_ext::VariantFieldIterMut<'a>),
    Value,
}

impl<'a> DynamicFieldIterMut<'a> {
    pub fn from_reflect_mut(ref_mut: ReflectMut<'a>) -> Self {
        match ref_mut {
            ReflectMut::Struct(s) => DynamicFieldIterMut::Struct(struct_ext::FieldIterMut::new(s)),
            ReflectMut::TupleStruct(s) => {
                DynamicFieldIterMut::TupleStruct(tuple_struct_ext::TupleStructFieldIterMut::new(s))
            }
            ReflectMut::Tuple(t) => {
                DynamicFieldIterMut::Tuple(tuple_ext::TupleFieldIterMut::new(t))
            }
            ReflectMut::List(l) => DynamicFieldIterMut::List(list_ext::ListIterMut::new(l)),
            ReflectMut::Array(a) => DynamicFieldIterMut::Array(array_ext::ArrayIterMut::new(a)),
            ReflectMut::Map(m) => DynamicFieldIterMut::Map(map_ext::MapIterMut::new(m)),
            ReflectMut::Enum(e) => DynamicFieldIterMut::Enum(enum_ext::VariantFieldIterMut::new(e)),
            ReflectMut::Value(_) => DynamicFieldIterMut::Value,
        }
    }
}

impl<'a> Iterator for DynamicFieldIterMut<'a> {
    type Item = &'a mut dyn Reflect;

    fn next(&mut self) -> Option<Self::Item> {
        match self {
            DynamicFieldIterMut::Struct(s) => s.next(),
            DynamicFieldIterMut::TupleStruct(s) => s.next(),
            DynamicFieldIterMut::Tuple(t) => t.next(),
            DynamicFieldIterMut::List(l) => l.next(),
            DynamicFieldIterMut::Array(a) => a.next(),
            DynamicFieldIterMut::Map(m) => m.next().map(|(_, v)| v),
            DynamicFieldIterMut::Enum(e) => e.next(),
            DynamicFieldIterMut::Value => None,
        }
    }
}
