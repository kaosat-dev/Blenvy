use bevy::reflect::{Reflect, Tuple};

pub struct TupleFieldIterMut<'a> {
    pub(crate) tuple: &'a mut dyn Tuple,
    pub(crate) index: usize,
}

impl<'a> TupleFieldIterMut<'a> {
    pub fn new(value: &'a mut dyn Tuple) -> Self {
        TupleFieldIterMut {
            tuple: value,
            index: 0,
        }
    }
}

impl<'a> Iterator for TupleFieldIterMut<'a> {
    type Item = &'a mut dyn Reflect;

    fn next(&mut self) -> Option<Self::Item> {
        let value = self.tuple.field_mut(self.index);
        self.index += value.is_some() as usize;
        value.map(|v| unsafe {
            // SAFETY: index can only correspond to one field
            &mut *(v as *mut _)
        })
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let size = self.tuple.field_len();
        (size, Some(size))
    }
}

impl<'a> ExactSizeIterator for TupleFieldIterMut<'a> {}
