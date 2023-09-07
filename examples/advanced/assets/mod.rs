pub mod assets_game;
pub use assets_game::*;

use bevy::prelude::*;
use bevy_asset_loader::prelude::*;

use crate::state::{AppState};

pub struct AssetsPlugin;
impl Plugin for AssetsPlugin {
  fn build(&self, app: &mut App) {
      app
      // .add_loading_state(LoadingState::new(AppState::CoreLoading).continue_to_state(AppState::MenuRunning))
      /* .add_dynamic_collection_to_loading_state::<_, StandardDynamicAssetCollection>(
        AppState::CoreLoading,
        "assets_core.assets.ron",
      )
      .add_collection_to_loading_state::<_, CoreAssets>(AppState::CoreLoading)*/

      .add_loading_state(LoadingState::new(AppState::AppLoading).continue_to_state(AppState::AppRunning))
      .add_dynamic_collection_to_loading_state::<_, StandardDynamicAssetCollection>(
        AppState::AppLoading,
        "assets_game.assets.ron",
      )
      .add_collection_to_loading_state::<_, GameAssets>(AppState::AppLoading)

    ;
    }
}