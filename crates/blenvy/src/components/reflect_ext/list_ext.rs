use bevy::reflect::{List, Reflect};

pub struct ListIterMut<'a> {
    list: &'a mut dyn List,
    index: usize,
}

impl<'a> ListIterMut<'a> {
    /// Creates a new [`ListIterMut`].
    #[inline]
    pub fn new(list: &'a mut dyn List) -> ListIterMut {
        ListIterMut { list, index: 0 }
    }
}

impl<'a> Iterator for ListIterMut<'a> {
    type Item = &'a mut dyn Reflect;

    #[inline]
    fn next(&mut self) -> Option<Self::Item> {
        let value = self.list.get_mut(self.index);
        self.index += value.is_some() as usize;
        value.map(|v| unsafe {
            // SAFETY: index can only correspond to one field
            &mut *(v as *mut _)
        })
    }

    #[inline]
    fn size_hint(&self) -> (usize, Option<usize>) {
        let size = self.list.len();
        (size, Some(size))
    }
}

impl<'a> ExactSizeIterator for ListIterMut<'a> {}
