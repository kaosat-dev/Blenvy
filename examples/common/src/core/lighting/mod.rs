use bevy::pbr::NotShadowCaster;
use bevy::prelude::*;

pub struct LightingPlugin;
impl Plugin for LightingPlugin {
    fn build(&self, app: &mut App) {
        app
            // FIXME: adding these since they are missing
            .register_type::<NotShadowCaster>();
    }
}
