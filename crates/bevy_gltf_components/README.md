[![Crates.io](https://img.shields.io/crates/v/bevy_gltf_components)](https://crates.io/crates/bevy_gltf_components)
[![Docs](https://img.shields.io/docsrs/bevy_gltf_components)](https://docs.rs/bevy_gltf_components/latest/bevy_gltf_components/)
[![License](https://img.shields.io/crates/l/bevy_gltf_components)](https://github.com/kaosat-dev/Blender_bevy_components_workflow/blob/main/crates/bevy_gltf_components/License.md)
[![Bevy tracking](https://img.shields.io/badge/Bevy%20tracking-released%20version-lightblue)](https://github.com/bevyengine/bevy/blob/main/docs/plugins_guidelines.md#main-branch-tracking)


# bevy_gltf_components

This crate allows you to define [Bevy](https://bevyengine.org/) components direclty inside gltf files and instanciate the components on the Bevy side.

## Usage

***important*** : the plugin for processing gltf files runs in ***update*** , so you cannot use the components directly if you spawn your scene from gltf in ***setup*** (the additional components will not show up)

Please see the 
 * [example](https://github.com/kaosat-dev/Blender_bevy_components_workflow/examples/basic) 
 * or use [```bevy_asset_loader```](https://github.com/NiklasEi/bevy_asset_loader) for a reliable workflow.
 * alternatively, use the [```bevy_gltf_blueprints```](https://github.com/kaosat-dev/Blender_bevy_components_workflow/blob/main/crates/bevy_gltf_blueprints) crate, build on this crate's features,
  that allows you to directly spawn entities from gltf based blueprints.

Here's a minimal usage example:

```toml
# Cargo.toml
[dependencies]
bevy="0.12"
bevy_gltf_components = { version = "0.2"} 

```

```rust no_run
//too barebones of an example to be meaningfull, please see https://github.com/kaosat-dev/Blender_bevy_components_workflow/examples/basic for a real example
 fn main() {
    App::new()
         .add_plugins(DefaultPlugins)
         .add_plugin(ComponentsFromGltfPlugin)
         .add_system(spawn_level)
         .run();
 }
 
 fn spawn_level(
   asset_server: Res<AssetServer>, 
   mut commands: bevy::prelude::Commands,
   keycode: Res<Input<KeyCode>>,

 ){
 if keycode.just_pressed(KeyCode::Return) {
  commands.spawn(SceneBundle {
   scene: asset_server.load("basic/models/level1.glb#Scene0"),
   transform: Transform::from_xyz(2.0, 0.0, -5.0),
 ..Default::default()
 });
 }
}

```

##  Installation

Add the following to your `[dependencies]` section in `Cargo.toml`:

```toml
bevy_gltf_components = "0.1"
```

Or use `cargo add`:

```toml
cargo add bevy_gltf_components
```

## SystemSet

the ordering of systems is very important ! 

For example to replace your proxy components (stand-in components when you cannot/ do not want to use real components in the gltf file) with actual ones, 

which should happen **AFTER** the components from the gltf files have been injected, 

so ```bevy_gltf_components``` provides a **SystemSet** for that purpose:[```GltfComponentsSet```](./src/lib.rs#46)

Typically , the order of systems should be

***bevy_gltf_components (GltfComponentsSet::Injection)*** => ***replace_proxies***

## Examples

https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/basic



## Compatible Bevy versions

The main branch is compatible with the latest Bevy release, while the branch `bevy_main` tries to track the `main` branch of Bevy (PRs updating the tracked commit are welcome).

Compatibility of `bevy_gltf_components` versions:
| `bevy_gltf_components` | `bevy` |
| :--                 | :--    |
| `0.2`               | `0.12` |
| `0.1`               | `0.11` |
| branch `main`       | `0.12` |
| branch `bevy_main`  | `main` |


## License

This crate, all its code, contents & assets is Dual-licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](./LICENSE_APACHE.md) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](./LICENSE_MIT.md) or https://opensource.org/licenses/MIT)