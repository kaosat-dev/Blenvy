pub mod camera;
pub use camera::*;

//pub mod relationships;
//pub use relationships::*;

#[cfg(feature = "physics_rapier")]
#[allow(ambiguous_glob_reexports)]
pub mod physics_rapier;
#[cfg(feature = "physics_rapier")]
pub use physics_rapier::*;

#[cfg(feature = "physics_xpbd")]
#[allow(ambiguous_glob_reexports)]
pub mod physics_xpbd;
#[cfg(feature = "physics_xpbd")]
pub use physics_xpbd::*;

use bevy::prelude::*;

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins(CameraPlugin);
        
        #[cfg(feature = "physics_rapier")]
        app.add_plugins(PhysicsPlugin);

        #[cfg(feature = "physics_xpbd")]
        app.add_plugins(PhysicsPluginXPBD);
        

    }
}
