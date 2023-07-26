use std::collections::HashSet;
use bevy::{prelude::*, asset::LoadState};
use bevy::gltf::Gltf;

use super::gltf_extras_to_components;

#[derive(Resource)]
  pub struct GltfLoadingTracker{
    pub loading_gltfs: HashSet<Handle<Gltf>>,
    pub loaded_gltfs: HashSet<Handle<Gltf>>
  }

  impl GltfLoadingTracker {
      pub fn new() -> GltfLoadingTracker {
        GltfLoadingTracker  {
          loaded_gltfs :  HashSet::new(),
          loading_gltfs: HashSet::new()
        }
      }
      pub fn add_scene(&mut self, handle: Handle<Gltf>) {
        self.loading_gltfs.insert(handle);
      }
  }
  

  pub fn track_new_gltf(
    mut tracker: ResMut<GltfLoadingTracker>,
    mut events: EventReader<AssetEvent<Gltf>>,
  ) {
    for event in events.iter() {
        if let AssetEvent::Created { handle } = event {
            tracker.add_scene(handle.clone());
            debug!("gltf created {:?}", handle.clone());
        }
    }
    events.clear();
}

  pub fn process_loaded_scenes(
    mut gltfs: ResMut<Assets<Gltf>>,
    mut scenes: ResMut<Assets<Scene>>,
    mut tracker: ResMut<GltfLoadingTracker>,
    app_type_registry: Res<AppTypeRegistry>,
    asset_server: Res<AssetServer>,

  ) {
    
    let mut loaded_gltfs = Vec::new();
    for gltf in &tracker.loading_gltfs {
      info!("checking for loaded gltfs {:?}", asset_server.get_load_state(gltf));

        if asset_server.get_load_state(gltf.clone()) == LoadState::Loaded {
          debug!("Adding scene to processing list");
            loaded_gltfs.push(gltf.clone());
        }
    }

    let type_registry = app_type_registry.read();

    for gltf_handle in &loaded_gltfs {
        if let Some(gltf) = gltfs.get_mut(gltf_handle) {

          // TODO this is a temporary workaround for library management 
          if let Some(asset_path) = asset_server.get_handle_path(gltf_handle) {
            let gltf_name = asset_path.path().file_stem().unwrap().to_str().unwrap();
            gltf_extras_to_components(gltf, &mut scenes, &*type_registry, &gltf_name);
            //gltf_extras_to_prefab_infos(gltf, &mut scenes, &*type_registry, &gltf_name);
          }
          else {
            gltf_extras_to_components(gltf, &mut scenes, &*type_registry, "");
          }
        }
        tracker.loading_gltfs.remove(gltf_handle);
        tracker.loaded_gltfs.insert(gltf_handle.clone());
        debug!("Done loading scene");
    }
  
  }

