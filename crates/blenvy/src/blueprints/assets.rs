use std::path::{Path, PathBuf};

use bevy::{asset::LoadedUntypedAsset, gltf::Gltf, prelude::*, utils::HashMap};
use serde::Deserialize;

use crate::{BlenvyConfig, BlueprintAnimations};

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug, Deserialize)]
#[reflect(Component)]
pub struct MyAsset{
    pub name: String,
    pub path: String
}

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug, Deserialize)]
#[reflect(Component)]
pub struct BlueprintAssets {
    /// only this field should get filled in from the Blender side
    pub assets: Vec<MyAsset>,
    /// set to default when deserializing
    #[serde(default)]
    #[reflect(default)]
    pub loaded: bool,
    /// set to default when deserializing
    #[serde(default)]
    #[reflect(default)]
    pub progress: f32,
    #[reflect(ignore)] 
    #[serde(skip)]
    pub asset_infos: Vec<AssetLoadTracker>,
}
//(pub Vec<MyAsset>);



////////////////////////
/// 
/// flag component, usually added when a blueprint is loaded
#[derive(Component)]
pub(crate) struct BlueprintAssetsLoaded;
/// flag component
#[derive(Component)]
pub(crate) struct BlueprintAssetsNotLoaded;

/// helper component, for tracking loaded assets's loading state, id , handle etc
#[derive(Debug, Reflect)]
pub(crate) struct AssetLoadTracker {
    #[allow(dead_code)]
    pub name: String,
    pub path: String,
    pub id: AssetId<LoadedUntypedAsset>,
    pub loaded: bool,
    #[allow(dead_code)]
    pub handle: Handle<LoadedUntypedAsset>,
}

/// helper component, for tracking loaded assets
#[derive(Component, Debug)]
pub(crate) struct BlenvyAssetsLoadState {
    pub all_loaded: bool,
    pub asset_infos: Vec<AssetLoadTracker>,
    pub progress: f32,
}
impl Default for BlenvyAssetsLoadState {
    fn default() -> Self {
        Self {
            all_loaded: Default::default(),
            asset_infos: Default::default(),
            progress: Default::default(),
        }
    }
}
