
# Nested blueprints example/demo

Example of blueprints (and thus gltf) nested & reuse to avoid redundant data in blueprints gltfs that lead to asset & memory bloat
- ideally, to be used together with ```gltf_auto_export``` version >0.8  with the "export nested blueprints" option for exports, as that will generate whole 
gltf blueprints hierarchies, and minimise their size for you
- It shows you how ou can configure```Bevy_gltf_blueprints``` to spawn nested blueprints


## Running this example

```
cargo run --features bevy/dynamic_linking
```
