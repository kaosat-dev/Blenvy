use std::path::{Path, PathBuf};

use bevy::{asset::LoadedUntypedAsset, gltf::Gltf, prelude::*, utils::HashMap};

use crate::{BluePrintsConfig, BlueprintAnimations};

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct MyAsset {
    pub name: String,
    pub path: String,
}

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct LocalAssets(pub Vec<MyAsset>);

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct BlueprintAssets(pub Vec<MyAsset>);

////////////////////////
///
/// flag component, usually added when a blueprint is loaded
#[derive(Component)]
pub(crate) struct BlueprintAssetsLoaded;
/// flag component
#[derive(Component)]
pub(crate) struct BlueprintAssetsNotLoaded;

/// helper component, for tracking loaded assets's loading state, id , handle etc
#[derive(Debug)]
pub(crate) struct AssetLoadTracker {
    #[allow(dead_code)]
    pub name: String,
    pub id: AssetId<LoadedUntypedAsset>,
    pub loaded: bool,
    #[allow(dead_code)]
    pub handle: Handle<LoadedUntypedAsset>,
}

/// helper component, for tracking loaded assets
#[derive(Component, Debug)]
pub(crate) struct AssetsToLoad {
    pub all_loaded: bool,
    pub asset_infos: Vec<AssetLoadTracker>,
    pub progress: f32,
}
impl Default for AssetsToLoad {
    fn default() -> Self {
        Self {
            all_loaded: Default::default(),
            asset_infos: Default::default(),
            progress: Default::default(),
        }
    }
}
