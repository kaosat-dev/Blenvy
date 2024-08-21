use bevy::reflect::{Array, Reflect};

pub struct ArrayIterMut<'a> {
    array: &'a mut dyn Array,
    index: usize,
}

impl<'a> ArrayIterMut<'a> {
    /// Creates a new [`ArrayIterMut`].
    #[inline]
    pub fn new(array: &'a mut dyn Array) -> ArrayIterMut {
        ArrayIterMut { array, index: 0 }
    }
}

impl<'a> Iterator for ArrayIterMut<'a> {
    type Item = &'a mut dyn Reflect;

    #[inline]
    fn next(&mut self) -> Option<Self::Item> {
        let value = self.array.get_mut(self.index);
        self.index += value.is_some() as usize;
        value.map(|v| unsafe {
            // SAFETY: index can only correspond to one field
            &mut *(v as *mut _)
        })
    }

    #[inline]
    fn size_hint(&self) -> (usize, Option<usize>) {
        let size = self.array.len();
        (size, Some(size))
    }
}

impl<'a> ExactSizeIterator for ArrayIterMut<'a> {}
