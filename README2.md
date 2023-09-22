[![Bevy tracking](https://img.shields.io/badge/Bevy%20tracking-released%20version-lightblue)](https://github.com/bevyengine/bevy/blob/main/docs/plugins_guidelines.md#main-branch-tracking)


# Blender_bevy_components_worklflow

![demo](./docs/blender_gltf_components.png)

Crates & tools for adding components from gltf files in the [Bevy](https://bevyengine.org/) game engine.

It enables minimalistic [Blender](https://www.blender.org/) (gltf) centric workflow for Bevy, ie defining entites & their components
inside Blender using Blender's objects **custom properties**. 
Aka "Blender as editor for Bevy"

It also allows you to setup 'blueprints' in Blender by using collections (the recomended way to go most of the time), or directly on single use objects .

## Features

* Useful if you want to use Blender (or any editor allowing to export gltf with configurable gltf_extras) as your Editor
* define Bevy components as custom properties in Blender (RON, though an older JSON version is also available)
* no plugin or extra tools needed in Blender (but I provide a little Blender plugin to auto-export to gltf on save if you want !)
* define components in Blender Collections & override any of them in your collection instances if you want
* minimal setup & code,  you can have something basic running fast

## Crates

- [bevy_gltf_components]('./crates/bevy_gltf_components/) This crate allows you to define components direclty inside gltf files and instanciate/inject the components on the Bevy side.

- [bevy_gltf_blueprints]('./crates/bevy_gltf_blueprints/) This crate adds the ability to define Blueprints/Prefabs for Bevy inside gltf files and spawn them in Bevy. With the ability to override and add components when spawning.