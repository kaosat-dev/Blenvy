use bevy::reflect::{Reflect, Struct};

/// An iterator over the field values of a struct.
pub struct FieldIterMut<'a> {
    pub(crate) struct_val: &'a mut dyn Struct,
    pub(crate) index: usize,
}

impl<'a> FieldIterMut<'a> {
    pub fn new(value: &'a mut dyn Struct) -> Self {
        FieldIterMut {
            struct_val: value,
            index: 0,
        }
    }
}

impl<'a> Iterator for FieldIterMut<'a> {
    type Item = &'a mut dyn Reflect;

    fn next(&mut self) -> Option<Self::Item> {
        let value = self.struct_val.field_at_mut(self.index);
        self.index += value.is_some() as usize;
        value.map(|v| unsafe {
            // SAFETY: index can only correspond to one field
            &mut *(v as *mut _)
        })
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let size = self.struct_val.field_len();
        (size, Some(size))
    }
}

impl<'a> ExactSizeIterator for FieldIterMut<'a> {}
