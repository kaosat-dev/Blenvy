use bevy::reflect::{Map, Reflect};

pub struct MapIterMut<'a> {
    map: &'a mut dyn Map,
    index: usize,
}

impl<'a> MapIterMut<'a> {
    /// Creates a new [`MapIterMut`].
    #[inline]
    pub fn new(map: &'a mut dyn Map) -> MapIterMut {
        MapIterMut { map, index: 0 }
    }
}

impl<'a> Iterator for MapIterMut<'a> {
    type Item = (&'a dyn Reflect, &'a mut dyn Reflect);

    fn next(&mut self) -> Option<Self::Item> {
        let value = self.map.get_at_mut(self.index);
        self.index += value.is_some() as usize;
        value.map(|(k, v)| unsafe {
            // SAFETY: index can only correspond to one field
            (&*(k as *const _), &mut *(v as *mut _))
        })
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let size = self.map.len();
        (size, Some(size))
    }
}

impl<'a> ExactSizeIterator for MapIterMut<'a> {}
