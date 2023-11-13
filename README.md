[![Bevy tracking](https://img.shields.io/badge/Bevy%20tracking-released%20version-lightblue)](https://github.com/bevyengine/bevy/blob/main/docs/plugins_guidelines.md#main-branch-tracking)
[![License](https://img.shields.io/crates/l/bevy_gltf_components)](https://github.com/kaosat-dev/Blender_bevy_components_workflow/blob/main/LICENSE.md)


# Blender_bevy_components_workflow

![demo](./docs/blender_gltf_components.png)

Crates & tools for adding components from gltf files in the [Bevy](https://bevyengine.org/) game engine.

It enables minimalistic [Blender](https://www.blender.org/) (gltf) centric workflow for Bevy, ie defining entites & their components
inside Blender using Blender's objects **custom properties**. 
Aka "Blender as editor for Bevy"

It also allows you to setup 'blueprints' in Blender by using collections (the recomended way to go most of the time), or directly on single use objects .

## Features

* Useful if you want to use Blender (or any editor allowing to export gltf with configurable gltf_extras) as your Editor
* define Bevy components as custom properties in Blender (some visually , some using RON, though an older JSON version is also available)
* no plugin or extra tools needed in Blender (but I provide a [little Blender plugin](./tools/gltf_auto_export/README.md) to auto-export to gltf on save (and more !) if you want !)
* define components in Blender Collections & override any of them in your collection instances if you want
* ability to automatically turn your Blender collections into [gltf Blueprints](./crates/bevy_gltf_blueprints/README.md) for reuse
* minimal setup & code,  you can have something basic running fast
* minimal dependencies: Bevy, Serde & Ron only !
* opensource 


## Crates

- [bevy_gltf_components](./crates/bevy_gltf_components/) This crate allows you to define components direclty inside gltf files and instanciate/inject the components on the Bevy side.
There is a [video tutorial/explanation](https://youtu.be/-lcScjQCA3c) if you want, or you can read the crate docs.
The examples for the crate are [here](./examples/bevy_gltf_components/)

- [bevy_gltf_blueprints](./crates/bevy_gltf_blueprints/) This crate adds the ability to define Blueprints/Prefabs for Bevy inside gltf files and spawn them in Bevy. With the ability to override and add components when spawning, efficient "level" loading etc
There is a [video tutorial/explanation](https://youtu.be/CgyNtwgYwdM) for this one too, or you can read the crate docs
The examples for the crate are [here](./examples/bevy_gltf_blueprints/)
> Note: this is the recomended crate to use and uses ```bevy_gltf_components``` under the hood


## Tools

### Blender: gltf_auto_export

- for convenience I also added a [Blender addon](./tools/gltf_auto_export/README.md) that automatically exports your level/world from Blender to gltf whenever you save your Blend file
- it also supports automatical exports of collections as [Gltf blueprints](./crates/bevy_gltf_blueprints/README.md) & more !

Please read the [README]((./tools/gltf_auto_export/README.md)) of the add-on for installation & use instructions


## Examples

you can find all examples, by crate as seperate crates for clearer dependencies in [here](./examples/)

- [bevy_gltf_components](./examples/bevy_gltf_components/) 
    * [basic](./examples/bevy_gltf_components/basic/) use of ```bevy_gltf_components``` only, to spawn entities with components defined inside gltf files

- [bevy_gltf_blueprints](./examples/bevy_gltf_blueprints/) 
    * [basic](./examples/bevy_gltf_blueprints/basic/) more advanced example : use of ```bevy_gltf_blueprints``` to spawn a level and then populate it with entities coming from different gltf files, live (at runtime) spawning of entities etc
    * [animation](./examples/bevy_gltf_blueprints/animation/) how to use and trigger animations from gltf files (a feature of ```bevy_gltf_blueprints```)

## Workflow

The workflow goes as follows (once you got your Bevy code setup)

- create & register all your components you want to be able to set from the Blender side (this is basic Bevy, no specific work needed)

![component registration](./docs/component_registration.png)
- Create an object / collection (for reuse) in Blender
- Go to object properties => add a property, and add your component data
    - unit structs, enums, and more complex strucs / components are all supported, (if the fields are basic data types at least,
    have not tried more complex ones yet, but should also work)
        - for structs with no params (unit structs): use a **STRING** property & an empty value 
        - for structs with params: use a RON representation of your fields (see below) 
        - for tupple strucs you can use any of the built in Blender custom property types: Strings, Booleans, floats, Vectors, etc

        ![unit struct components in Blender](./docs/components_blender.png)

        In rust:

        ![unit struct components in Bevy](./docs/demo_simple_components.png)

        (the Rust struct for these components for reference is [here](./examples/basic/game.rs#34) )


        ![complex components in Blender](./docs/components_blender_parameters.png)

        In rust:

        ![complex components in Blender](./docs/camera_tracking_component.png)

        (the Rust struct for this component for reference is [here](./examples/basic/core/camera/camera_tracking.rs#21) )

        There is an other examples of using various Component types: Enums, Tupple structs,  strucs with fields etc [here](./examples/basic/test_components.rs),
        even colors, Vecs (arrays), Vec2, Vec3 etc are all supported

        ![complex components in Blender](./docs/components_blender_parameters2.png)

- for collections & their instances: 
    * I usually create a library scene with nested collections
        * the leaf collections are the assets you use in your level
        * add an empty called xxxx_components
        * add the components as explained in the previous part
        
        ![blender collection asset](./docs/blender_collections.png)

    * In the Level/world itself, just create an instance of the collection (standard Blender, ie Shift+A -> collection instance -> pick the collection)


- export your level as a glb/gltf file :
    - using Blender's default gltf exporter
        !!**IMPORTANT** you need to check the following:
        - custom properties
        - cameras & lights if you want a complete level (as in this example)
        ![gltf_export](./docs/gltf_export.png)
    - or much better, using [gltf_auto_export](./tools/gltf_auto_export/)



- load it in Bevy (see the demo main file for this)
- you should see the components attached to your entities in Bevy

![components in bevy](./docs/components_bevy.png)
![components in bevy](./docs/components_bevy2.png)
![components in bevy](./docs/components_bevy3.png)


> note: you get a warning if there are any unregistered components in your gltf file (they get ignored)
you will get a warning **per entity**

![missing components warnings](./docs/component_warnings.png)



## Limitations / issues
- some components have to be defined in ```text``` in Blender, might try using the AppTypeRegistry and some Python code on the Blender side for a nicer UI (although this loses the "fast & easy, no tooling" approach)
- Some of `bevy_rapier`/physics code / ways to define colliders could perhaps be done better/visually within Blender (currently it also goes via RON)

## Future work
- I have a number of other tools/ code  helpers that I have not yet included here, because they need cleanup/ might make this example too complex

## Credits

- somebody I cannot recall helped me originally with the gltf loading tracker in the Bevy Discord, so thanks ! And if it was you, please let me know so I can give credit where credit is due :)

## Contributors

Thanks to all the contributors helping out with this project ! Big kudos to you, contributions are always appreciated ! :)

- [GitGhillie](https://github.com/GitGhillie)
- [Azorlogh](https://github.com/Azorlogh)

## License

This repo, all its code, contents & assets is Dual-licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](./LICENSE_APACHE.md) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](./LICENSE_MIT.md) or https://opensource.org/licenses/MIT)
