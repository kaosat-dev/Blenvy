pub mod assets_core;
pub use assets_core::*;

pub mod assets_game;
pub use assets_game::*;

use bevy::prelude::*;
use bevy_asset_loader::prelude::*;

use crate::state::AppState;

pub struct AssetsPlugin;
impl Plugin for AssetsPlugin {
    fn build(&self, app: &mut App) {
        app
            // load core assets (ie assets needed in the main menu, and everywhere else before loading more assets in game)
            .add_loading_state(
                LoadingState::new(AppState::CoreLoading)
                    .continue_to_state(AppState::MenuRunning)
                    .with_dynamic_assets_file::<StandardDynamicAssetCollection>(
                        "assets_core.assets.ron",
                    )
                    .load_collection::<CoreAssets>(),
            )
            // load game assets
            .add_loading_state(
                LoadingState::new(AppState::AppLoading)
                    .continue_to_state(AppState::AppRunning)
                    .with_dynamic_assets_file::<StandardDynamicAssetCollection>(
                        "assets_game.assets.ron",
                    )
                    .load_collection::<GameAssets>(),
            );
    }
}
