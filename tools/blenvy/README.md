# Blenvy: Blender add-on


This [Blender addon](https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/tools/blenvy) gives you:
- an easy to use UI to add and configure your [Bevy](https://bevyengine.org/) components inside Blender 
    - the UI is **automatically generated** based on a **registry schema** file, an export of all your **registered** Bevy components's information, generated
by the registry export part of the [Blenvy](https://crates.io/crates/blenvy) crate
    - the ability to **toggle components** on/off without having to remove the component from the object
- an easy way to create blueprints/prefabs (just collections !) & levels 
- a way to setup you assets for your levels & blueprints
- an automatic export of your level/world from Blender to gltf whenever you save your Blend file.
    - export of used /marked collections as [Gltf blueprints](../../crates/blenvy/README.md)
    - change detection, so that only the levels & blueprints you have changed get exported when you save your blend file
    - export of material librairies


If you want to know more about the technical details , see [here]()

> IMPORTANT !! if you have previously used the "old" add-ons (*gltf_auto_export* & *bevy_components*), please see the [migration guide](../../Migration_guide.md)
If you can I would generally recommend starting fresh, but a lot of effort has been put to make transitioning easier


## Installation: 


* grab the latest release zip file

![blender addon install](./docs/blender_addon_install_zip.png)


* in Blender go to edit =>  preferences => install

![blender addon install](./docs/blender_addon_install.png)

* choose the path where ```blenvy.zip``` is stored

![blender addon install](./docs/blender_addon_install2.png)

  * up to Blender 4.1
  * for Blender 4.2 , just drag & drop the zip file onto Blender to start the installation process


## Quickstart

* set your level & library scenes (the only things that are not pre-configured)

![blenvy common settings](./docs/blenvy_configuration_common.png)

* create your blueprints & levels
* add components (remember to configure the Bevy side first )
* save your blend file at any point , the rest is done automatically (export of levels & blueprints, etc)


## Configuration:

### Bevy side

 - setup the [Blenvy crate](https://crates.io/crates/blenvy) for your project (see the crate's documentation for that), and compile/run it to get the ```registry.json``` file to enable adding/editing your components in Blender

### Blender side


> The add-on comes almost completely pre-configured with sensible defaults, but you can set the following settings to your liking

#### Common

The first tab (and the one that is open by default in a new project) contains the common settings:

![blenvy common settings](./docs/blenvy_configuration_common.png)

you **need** to tell Blenvy 

  - what your level scenes are (what Blender scenes should become levels in Bevy) 
  - what your library scenes are (what Blender scenes will store your library of re-useable blueprints) 

Blenvy is opinionated ! 

  - keep you art/sources (usually not delivered with your game) seperate from your game assets
  - keep your blueprints/levels/materials gltf files seperate

##### Root Folder (default: ../)

- this is the same folder as your Bevy projects main folder: the path here is relative to the current .blend file

##### Assets Folder (default: ./assets)

- a path, relative to the *root* folder above, where you want to store your assets (delivered with your game)

##### Blueprints Folder (default: blueprints)

- a path, relative to the *assets* folder above, where you want to store your *blueprints*

##### Levels Folder (default: levels)

- a path, relative to the *assets* folder above, where you want to store your *levels*

##### Materials Folder (default: materials)

- a path, relative to the *assets* folder above, where you want to store your *materials*

##### Level scenes

  -  what are the scenes in your .blend file that are levels/worlds

##### library scenes

  - library scenes: what are the scenes in your .blend file that contain your libraries of blueprints (that you then use in your levels)


#### Recomended folder structure

![recomended folder structure](./docs/blenvy_recommended_folder_structure.png)

![recomended folder structure art](./docs/blenvy_recommended_folder_structure_art.png)

![recomended folder structure assets](./docs/blenvy_recommended_folder_structure_assets.png)


#### Components

The second tab contains the component settings:

![blenvy component settings](./docs/blenvy_configuration_components.png)


> you normally do not need to do anything, as the defaults are already pre-set to match those on the Bevy side for the location of the ```registry.json``` file, unless you want to store it somewhere other than ```assets/registry.json```

###### registry file (default: assets/registry.json)

- click on the button to select your registry.json file (in the "configuration" panel)

###### reload registry

- click on the button to force refresh the list of components from the registry.json file


##### registry file polling

* by default, the add-on will check for changes in your registry file every second, and refresh the UI accordingly
* you can set the polling frequency or turn it off if you do not want auto-refresh

#### Export

Last but not least, the export/ auto-export settings tab

![blenvy export settings](./docs/blenvy_configuration_export.png)

##### Auto export (default: True)

- toggle this to turn the whole auto-export system on or off : 
 when enabled, **every time you save your blend file** Blenvy will automatically export a set of gltf files , for levels, blueprints, materials etc depending on your settings, see below.

##### Gltf settings

- click on this button to open Blender's standard gltf exporter settings **specific to Blenvy** : ie you have access to all of the normal gltf settings, but there is additional boilerplate
to gather these settings for Blenvy only, so it does not impact your normal export settings
- you *must* keep the "remember export settings" checkbox checked in order for the settings to be useable by Blenvy

> Important ! Do not use Blender's default gltf exporter (under file => export => gltf), as it does not impact Blenvy's settings

##### Export scene settings (default: True)

- toggle this to export additional settings like ambient color, bloom, ao, etc from Blender to Bevy: this automatically generates additional components at the scene level that get processed by the Blenvy crate

##### Use change detection (default: True)

- toggle this to enable change detection: ie, to make sure that only the blueprints , levels or materials that have actually **changed since your last save** get exported to gltf files, a sort of "incremental export".

> Under the hood, Blenvy serializes your whole Blender project to a simplified representation, to be able to tell the differents between successive changes

##### Detailed materials scan (default: True)

- this options enables more detailed materials scanning & thus detecting smaller changes, even **changes in material nodes** . This comes at a potential additional processing cost, so if you notice performance issues in projects with complex materials
you can turn this off

##### Detailed modifiers scan (default: True)

- similar to the one above but for modifiers, this options enables more finer grained change detection in modifiers, even **changes in geometry nodes** . This comes at a potential additional processing cost, so if you notice performance issues in projects with complex modifiers
you can turn this off

##### Export blueprints (default: True)

- check this if you want to automatically export blueprints 

##### Collection instances (default: split)

select which option you want to use to deal with collection instances (aka combine mode) (both inside blueprint collections & main collections)

  * split (default, highly recomended) : the addon will 'split out' any nested collections/ blueprints & export them
  * embed: choose this option if you want to keep everything inside a gltf file (less efficient, not recomended)
  * embedExternal: this will embed ONLY collection instances whose collections have not been found inside the current blend file

  These options can also be **overridden** on a per collection instance basis: (if you want to split out most collection instances, but keep a few specific ones embeded
  inside your gltf file)
      
  ![combine override](./docs/combine_override.png) 

  - simply add a custom property called **_combine** to the collection instance, and set it to one of the options above

##### Export dynamic and static objects seperatly (default: False)
 

For levels scenes only, toggle this to generate 2 files per level: 

  - one with all dynamic data: collections or instances marked as dynamic (aka saveable)
  - one with all static data: anything else that is NOT marked as dynamic, the file name will have the suffix **_dynamic**

  Ie if you add a **Dynamic** custom/ component to either your collection instances or your blueprint, you get a clean seperation between 

  - your static level data (anything that will never change during the lifetime of your Bevy app)
  - your dynamic objects (anything that will change during the lifetime of your Bevy app, that can be saved & reloaded in save files for example)

##### export materials library (default: True)

check this if you want to automatically export material libraries 
please read the dedicated [section](./README-export.md#materials) below for more information

#### Additional export settings

- you can also force per level or per blueprint systematic export (regardless of change detection), see the relevant sections in the levels & blueprint documentation

### Multiple blend file workflow

If you want to use multiple blend files (recomended if your project starts to grow even a bit), use Blender's asset library etc, we got you coverred too !
There are only a few things to keep in mind 

#### Assets/library/blueprints files
- mark your library scenes as specified above, but **do NOT** specify a **level** scene
- mark any collection in your scenes as "assets"
- choose "split" for the combine mode (as you want your gltf blueprints to be saved for external use)
- do your Blender things as normal
- anytime you save your file, it will automatically export any relevant collections/blueprints
- (optional) activate the **material library** option, so you only have one set of material per asset library (recomended)

#### Level/world files
- mark your level scenes as specified above ( personally I recommended **NOT** specifying a **library** scene in this case to keep things tidy, but that is up to you)
- configure your asset libraries as you would usually do, I recomend using the "link" mode so that any changes to asset files are reflected correctly
- drag & drop any assets from the blueprints library (as you would normally do in Blender as well)
- choose "split" for the combine mode (as you want your gltf blueprints to be external usually & use the gltf files generated from your assets library)
- do your Blender things as normal
- anytime you save your file, it will automatically export your level(s)

Take a look at the [relevant](../../examples/demo/) example for more [details](../../examples/demo/art/) 


## Useage

### Components

- for a detailed overview on how to add, edit, remove etc components please see [here](./README-components.md)

### Export

- for a detailed overview on auto exporting gltf files please see [here](./README-export.md)

### Levels

- for a detailed overview of blueprints please see [here](./README-levels.md)


### Blueprints

- for a detailed overview of blueprints please see [here](./README-blueprints.md)

## Development 

- I highly recomend (if you are using vscode like me) to use 
[this](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development) excellent extension , works easilly and fast , even for the latest 
versions of Blender (v4.0 as of this writing)
- this [article](https://polynook.com/learn/set-up-blender-addon-development-environment-in-windows) might also help out 
(easy enough to get it working on linux too)

## License

This tool, all its code, contents & assets is Dual-licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](../LICENSE_APACHE.md) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](../LICENSE_MIT.md) or https://opensource.org/licenses/MIT)