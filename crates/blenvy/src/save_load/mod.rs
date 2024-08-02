use bevy::prelude::*;

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
/// component used to mark any entity as Dynamic: aka add this to make sure your entity is going to be saved
pub struct Dynamic;

#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
/// marker component for entities that do not have parents, or whose parents should be ignored when serializing
pub(crate) struct RootEntity;

#[derive(Component, Debug)]
/// internal helper component to store parents before resetting them
pub(crate) struct OriginalParent(pub(crate) Entity);


/// Marker component to Flag the root entity of all static entities (immutables)
#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct StaticEntitiesRoot;

/// Marker component to Flag the root entity of all dynamic entities (mutables)
#[derive(Component, Reflect, Debug, Default)]
#[reflect(Component)]
pub struct DynamicEntitiesRoot;


#[derive(Resource, Clone, Debug, Default, Reflect)]
#[reflect(Resource)]
pub struct StaticEntitiesBlueprintInfo {
    //pub blueprint_info: BlueprintInfo,
    pub path: String,
}


pub mod saving;
pub use saving::*;

#[derive(Debug, Clone, Default)]
/// Plugin for saving & loading
pub struct SaveLoadPlugin {}

impl Plugin for SaveLoadPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<Dynamic>()
            .register_type::<StaticEntitiesRoot>()

            .add_event::<SaveRequest>()
            .add_event::<SaveFinished>()
            .add_systems(
                Update,
                (prepare_save_game, apply_deferred, save_game, cleanup_save)
                    .chain()
                    .run_if(should_save),
            )
        ;
    }
}
