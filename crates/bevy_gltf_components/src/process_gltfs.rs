use bevy::asset::AssetPath;
use bevy::gltf::Gltf;
use bevy::utils::HashSet;
use bevy::{asset::LoadState, prelude::*};
use std::path::Path;

use crate::{gltf_extras_to_components, GltfComponentsConfig};

#[derive(Resource)]
/// component to keep track of gltfs' loading state
pub struct GltfLoadingTracker {
    pub loading_gltfs: HashSet<Handle<Gltf>>,
    pub processed_gltfs: HashSet<String>,
}
impl Default for GltfLoadingTracker {
    fn default() -> Self {
        Self::new()
    }
}

impl GltfLoadingTracker {
    pub fn new() -> GltfLoadingTracker {
        GltfLoadingTracker {
            loading_gltfs: HashSet::new(),
            processed_gltfs: HashSet::new(),
        }
    }
    pub fn add_gltf(&mut self, handle: Handle<Gltf>) {
        self.loading_gltfs.insert(handle);
    }
}

pub fn track_new_gltf(
    mut tracker: ResMut<GltfLoadingTracker>,
    mut events: EventReader<AssetEvent<Gltf>>,
    asset_server: Res<AssetServer>,
) {
    for event in events.read() {
        if let AssetEvent::Added { id } = event {
            let handle = asset_server.get_id_handle(*id);
            if let Some(handle) = handle {
                tracker.add_gltf(handle.clone());
                debug!("gltf created {:?}", handle);
            } else {
                let asset_path = asset_server
                    .get_path(*id)
                    .unwrap_or(AssetPath::from_path(Path::new("n/a"))); // will unfortunatly not work, will do a PR/ discussion at the Bevy level, leaving for reference, would be very practical
                warn!(
                    "a gltf file ({:?}) has no handle available, cannot inject components",
                    asset_path
                );
            }
        }
    }
    events.clear();
}

pub fn process_loaded_scenes(
    mut gltfs: ResMut<Assets<Gltf>>,
    mut tracker: ResMut<GltfLoadingTracker>,
    mut scenes: ResMut<Assets<Scene>>,
    app_type_registry: Res<AppTypeRegistry>,
    asset_server: Res<AssetServer>,
    gltf_components_config: Res<GltfComponentsConfig>,
) {
    let mut loaded_gltfs = Vec::new();
    for gltf in &tracker.loading_gltfs {
        debug!(
            "checking for loaded gltfs {:?}",
            asset_server.get_load_state(gltf)
        );

        if let Some(load_state) = asset_server.get_load_state(gltf.clone()) {
            if load_state == LoadState::Loaded {
                debug!("Adding scene to processing list");
                loaded_gltfs.push(gltf.clone());
            }
        }
    }

    let type_registry = app_type_registry.read();

    for gltf_handle in &loaded_gltfs {
        if let Some(gltf) = gltfs.get_mut(gltf_handle) {
            gltf_extras_to_components(
                gltf,
                &mut scenes,
                &*type_registry,
                gltf_components_config.legacy_mode,
            );

            if let Some(path) = gltf_handle.path() {
                tracker.processed_gltfs.insert(path.to_string());
            }
        } else {
            warn!("could not find gltf asset, cannot process it");
        }
        tracker.loading_gltfs.remove(gltf_handle);
        debug!("Done loading gltf file");
    }
}
