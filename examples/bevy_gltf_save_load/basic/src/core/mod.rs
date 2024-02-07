use bevy::{
    core_pipeline::tonemapping::Tonemapping,
    prelude::*,
    render::{camera::CameraRenderGraph, primitives::Frustum, view::VisibleEntities},
    utils::HashSet,
};
use bevy_gltf_blueprints::*;
use bevy_gltf_save_load::*;
use bevy_gltf_worlflow_examples_common::{CameraTrackingOffset, Pickable};
use bevy_rapier3d::dynamics::Velocity;
use std::any::TypeId;

pub struct CorePlugin;
impl Plugin for CorePlugin {
    fn build(&self, app: &mut App) {
        app.add_plugins((
            SaveLoadPlugin {
                save_path: "scenes".into(),
                component_filter: SceneFilter::Allowlist(HashSet::from([
                    TypeId::of::<Name>(),
                    TypeId::of::<Transform>(),
                    TypeId::of::<Velocity>(),
                    TypeId::of::<InheritedVisibility>(),
                    TypeId::of::<Camera>(),
                    TypeId::of::<Camera3d>(),
                    TypeId::of::<Tonemapping>(),
                    TypeId::of::<CameraTrackingOffset>(),
                    TypeId::of::<Projection>(),
                    TypeId::of::<CameraRenderGraph>(),
                    TypeId::of::<Frustum>(),
                    TypeId::of::<GlobalTransform>(),
                    TypeId::of::<VisibleEntities>(),
                    TypeId::of::<Pickable>(),
                ])),
                ..Default::default()
            },
            BlueprintsPlugin {
                library_folder: "models/library".into(),
                format: GltfFormat::GLB,
                aabbs: true,
                ..Default::default()
            },
        ));
    }
}
