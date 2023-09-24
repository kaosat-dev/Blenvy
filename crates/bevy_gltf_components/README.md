[![Crates.io](https://img.shields.io/crates/v/bevy_gltf_components)](https://crates.io/crates/bevy_gltf_components)
[![Docs](https://img.shields.io/docsrs/bevy_gltf_components)](https://docs.rs/bevy_gltf_components/latest/bevy_gltf_components/)
[![License](https://img.shields.io/crates/l/bevy_gltf_components)](https://github.com/kaosat-dev/Blender_bevy_components_worklflow/blob/main/crates/bevy_gltf_components/License.md)
[![Bevy tracking](https://img.shields.io/badge/Bevy%20tracking-released%20version-lightblue)](https://github.com/bevyengine/bevy/blob/main/docs/plugins_guidelines.md#main-branch-tracking)


# bevy_gltf_components

This crate allows you to define [Bevy](https://bevyengine.org/) components direclty inside gltf files and instanciate the components on the Bevy side.

## Usage

***important*** : the plugin for processing gltf files runs in ***update*** , so you cannot use the components directly if you spawn your scene from gltf in ***setup*** (the additional components will not show up)

Please see the included example or use [```bevy_asset_loader```](https://github.com/NiklasEi/bevy_asset_loader) for a reliable workflow.
Or alternatively, use the [```bevy_gltf_blueprints```](https://github.com/kaosat-dev/Blender_bevy_components_worklflow/blob/main/crates/bevy_gltf_blueprints) crate that allows you to directly spawn entities from gltf based blueprints.

Here's a minimal usage example:

```toml
# Cargo.toml
[dependencies]
bevy_gltf_components = { version = "0.3.0"} 

```

```rust no_run
use bevy::prelude::*;
use bevy_gltf_components::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugin(ComponentsFromGltfPlugin)

        .run();
}

```


## SystemSet

the ordering of systems is very important ! 

For example to replace your proxy components (stand-in components when you cannot/ do not want to use real components in the gltf file) with actual ones, 

which should happen **AFTER** the components from the gltf files have been injected, 

so ```bevy_gltf_components``` provides a **SystemSet** for that purpose:[```GltfComponentsSet```](./src/lib.rs#46)

Typically , the order of systems should be

***bevy_gltf_components (GltfComponentsSet::Injection)*** => ***replace_proxies***

## Examples

