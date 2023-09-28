# gltf_auto_export

For convenience I also added this [Blender addon](./gltf_auto_export.py) that 
- automatically exports your level/world from Blender to gltf whenever you save your Blend file.
- it also supports automatical exports of used collections as [Gltf blueprints](../../crates/bevy_gltf_blueprints/README.md) & more !
 

## Installation: 

* in Blender go to edit =>  preferences => install

![blender addon install](../../docs/blender_addon_install.png)

* choose the path where ```gltf_auto_export/gltf_auto_export.py``` is stored

![blender addon install](../../docs/blender_addon_install2.png)

## Usage: 


### Basics

* before it can automatically save to gltf, you need to configure it
* go to file => export => gltf auto export

![blender addon use](../../docs/blender_addon_use.png)

* set the autoexport parameters : output path, name of your main scene etc in the **auto export** panel

![blender addon use3](../../docs/blender_addon_use3.png)

* and your standard gltf export parameters in the **gltf** panel

![blender addon use2](../../docs/blender_addon_use2.png)


* click on "apply settings"
* now next time you save your blend file you will get an automatically exported gltf file (or more than one, depending on your settings, see below)

### Blueprints

You can enable this option to automatically replace all the **collection instances** inside your main scene with blueprints
- whenever you change your main scene (or your library scene , if that option is enabled), all your collection instances 
    * will be replaced with empties (this will not be visible to you)
    * those empties will have additional custom properties / components : ```BlueprintName``` & ```SpawnHere```
    * your main scene/ level will be exported to a much more trimmed down gltf file (see next point)
    * all the original collections (that you used to create the instances) will be exported as **seperate gltf files** into the "library" folder

- this means you will have 
    * one small main gltf file (your level/world)
    * as many gltf files as you have used collections in the main scene , in the library path you specified :
    for the included [advanced](../../examples/advanced/) example's [assets](../../assets/advanced/models/), it looks something like this: 

    ![library](../../docs/exported_library_files.png)
    
    the .blend file that they are generated from can be found [here](../../assets/advanced/advanced.blend)

#### Process

This is the internal logic of the export process with blueprints 

![process](../../docs/process.svg)

ie this is an example scene...

![](../../docs/workflow_original.jpg)

and what actually gets exported for the main scene/world/level

![](../../docs/workflow_empties.jpg)

all collections instances replaced with empties, and all those collections exported to gltf files as seen above


### TODO:

- [ ] add ability to have multiple main & library scenes
- [ ] detect which objects have been changed to only re-export those

## License

This tool, all its code, contents & assets is Dual-licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](../LICENSE_APACHE.md) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](../LICENSE_MIT.md) or https://opensource.org/licenses/MIT)