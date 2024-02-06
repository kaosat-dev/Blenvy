use bevy::gltf::Gltf;
use bevy::prelude::*;
use bevy::utils::HashMap;
use bevy_asset_loader::prelude::*;

#[derive(AssetCollection, Resource)]
pub struct GameAssets {
    #[asset(key = "world")]
    pub world: Handle<Gltf>,

    #[asset(key = "world_dynamic", optional)]
    pub world_dynamic: Option<Handle<Gltf>>,

    #[asset(key = "level1", optional)]
    pub level1: Option<Handle<Gltf>>,
    #[asset(key = "level2", optional)]
    pub level2: Option<Handle<Gltf>>,


    #[asset(key = "models", collection(typed, mapped))]
    pub models: HashMap<String, Handle<Gltf>>,

    #[asset(key = "materials", collection(typed, mapped), optional)]
    pub materials: Option<HashMap<String, Handle<Gltf>>>,
}
