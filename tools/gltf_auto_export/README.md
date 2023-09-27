# gltf_auto_export

For convenience I also added this [Blender addon](./gltf_auto_export.py) that automatically exports your level/world from Blender to gltf whenever you save your Blend file
(actually when you save inside your level/world scene or in the "library" scene, where I personally usually store all collections to instanciate).
It is **very** barebones and messy, but it does a minimal ok job.

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

* set up your parameters: output path, name of your main scene etc

    ![blender addon use2](../../docs/blender_addon_use2.png)

* click on "apply settings"
* now next time you save your blend file you will get an automatically exported gltf file

### Blueprints

You can enable this option to automatically replace all the **collection instances** inside your main scene with blueprints
- whenever you change your main scene (or your library scene , if that option is enabled), all your collection instances 
    * will be replaced with empties (this will not be visible to you)
    * those empties will have additional components : ```BlueprintName``` & ```SpawnHere```
    * your main scene/ level will be exported to a much more trimmed down gltf file (see next point)
    * all the original collections (that you used to create the instances) will be exported as **seperate gltf files** into the "library" folder


## Process

![process](../../docs/process.svg)


### TODO:

- [ ] add ability to have multiple main & library scenes
- [ ] detect which objects have been changed to only re-export those