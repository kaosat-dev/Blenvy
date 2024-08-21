use bevy::reflect::{Enum, Reflect};

pub struct VariantFieldIterMut<'a> {
    container: &'a mut dyn Enum,
    index: usize,
}

impl<'a> VariantFieldIterMut<'a> {
    pub fn new(container: &'a mut dyn Enum) -> Self {
        Self {
            container,
            index: 0,
        }
    }
}

impl<'a> Iterator for VariantFieldIterMut<'a> {
    // TODO: make this work with `VariantFieldMut` again
    type Item = &'a mut dyn Reflect;

    fn next(&mut self) -> Option<Self::Item> {
        let value = self.container.field_at_mut(self.index);
        self.index += value.is_some() as usize;
        value.map(|v| unsafe {
            // SAFETY: index can only correspond to one field
            &mut *(v as *mut _)
        })
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let size = self.container.field_len();
        (size, Some(size))
    }
}

impl<'a> ExactSizeIterator for VariantFieldIterMut<'a> {}
