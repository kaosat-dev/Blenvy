use std::path::{Path, PathBuf};

use bevy::{gltf::Gltf, prelude::*, utils::HashMap};

use crate::{BluePrintsConfig, BlueprintAnimations};

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct MyAsset{
    pub name: String,
    pub path: String
}

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct LocalAssets(pub Vec<MyAsset>);

/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct AllAssets(pub Vec<MyAsset>);



/// helper component, is used to store the list of sub blueprints to enable automatic loading of dependend blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct BlueprintsList(pub HashMap<String, Vec<String>>);

/// helper component, for tracking loaded assets's loading state, id , handle etc
#[derive(Default, Debug)]
pub(crate) struct AssetLoadTracker<T: bevy::prelude::Asset> {
    #[allow(dead_code)]
    pub name: String,
    pub id: AssetId<T>,
    pub loaded: bool,
    #[allow(dead_code)]
    pub handle: Handle<T>,
}

/// helper component, for tracking loaded assets
#[derive(Component, Debug)]
pub(crate) struct AssetsToLoad<T: bevy::prelude::Asset> {
    pub all_loaded: bool,
    pub asset_infos: Vec<AssetLoadTracker<T>>,
    pub progress: f32,
}
impl<T: bevy::prelude::Asset> Default for AssetsToLoad<T> {
    fn default() -> Self {
        Self {
            all_loaded: Default::default(),
            asset_infos: Default::default(),
            progress: Default::default(),
        }
    }
}

/// flag component, usually added when a blueprint is loaded
#[derive(Component)]
pub(crate) struct BlueprintAssetsLoaded;
/// flag component
#[derive(Component)]
pub(crate) struct BlueprintAssetsNotLoaded;
