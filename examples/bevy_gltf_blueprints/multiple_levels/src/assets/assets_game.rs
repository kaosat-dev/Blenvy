use bevy::gltf::Gltf;
use bevy::prelude::*;
use bevy::utils::HashMap;
use bevy_asset_loader::prelude::*;

#[derive(AssetCollection, Resource)]
pub struct GameAssets {
    #[asset(key = "world")]
    pub world: Handle<Gltf>,
    #[asset(key = "level1")]
    pub level1: Handle<Gltf>,
    #[asset(key = "level2")]
    pub level2: Handle<Gltf>,
    #[asset(key = "models", collection(typed, mapped))]
    pub models: HashMap<String, Handle<Gltf>>,
}
