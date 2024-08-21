use bevy::reflect::{Reflect, TupleStruct};

pub struct TupleStructFieldIterMut<'a> {
    pub(crate) tuple_struct: &'a mut dyn TupleStruct,
    pub(crate) index: usize,
}

impl<'a> TupleStructFieldIterMut<'a> {
    pub fn new(value: &'a mut dyn TupleStruct) -> Self {
        TupleStructFieldIterMut {
            tuple_struct: value,
            index: 0,
        }
    }
}

impl<'a> Iterator for TupleStructFieldIterMut<'a> {
    type Item = &'a mut dyn Reflect;

    fn next(&mut self) -> Option<Self::Item> {
        let value = self.tuple_struct.field_mut(self.index);
        self.index += value.is_some() as usize;
        value.map(|v| unsafe {
            // SAFETY: index can only correspond to one field
            &mut *(v as *mut _)
        })
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let size = self.tuple_struct.field_len();
        (size, Some(size))
    }
}

impl<'a> ExactSizeIterator for TupleStructFieldIterMut<'a> {}
