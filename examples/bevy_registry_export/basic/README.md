# Bevy registry export example/demo

This example showcases 
* the use of the bevy_registry_export crate to extract all components & types information into a json file.
* That file is then used by the [Blender addon](https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/tools/blenvy) to create Uis for each component,
to be able to add & edit Bevy components easilly in Blender !


## Running this example

```
cargo run --features bevy/dynamic_linking
```

Running the example also regenerates the registry.json file.
