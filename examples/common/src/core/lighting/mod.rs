mod lighting_replace_proxies;
use lighting_replace_proxies::*;

use bevy::pbr::NotShadowCaster;
use bevy::prelude::*;

pub struct LightingPlugin;
impl Plugin for LightingPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<AmbientLightSettings>()
            .register_type::<ShadowmapSettings>()
            // FIXME: adding these since they are missing
            .register_type::<NotShadowCaster>()
            .add_systems(PreUpdate, lighting_replace_proxies);
    }
}
