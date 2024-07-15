
## Usage: 

> ***IMPORTANT***

if you have used a version of this add-on prior to v0.9, there was an issue that kept generating orphan (junk) data on every save !
You can easilly clean up that data 

- go to orphan data:

![purge orphan data](./docs/purge_orphan1_data1.png)

- click on purge

![purge orphan data](./docs/purge_orphan1_data2.png)

- validate

![purge orphan data](./docs/purge_orphan1_data3.png)



This issue has been resolved in v0.9.


### Basics

* before it can automatically save to gltf, you need to configure it
* go to file => export => gltf auto export

![blender addon use](./docs/blender_addon_use.png)

* set the autoexport parameters  in the **auto export** panel: 

    ![blender addon use3](./docs/blender_addon_use3.png)


    - export folder: root folder to export models too
    - export scene settings: exports "global"/scene settings like ambient color, bloom, ao, etc 
        
        This automatically generates additional components at the scene level 

    - pick your main (level) scenes and/or library scenes (see the chapter about [Blueprints](#blueprints) and [multiple Blend filles workflow](#multiple-blend-file-workflow) below)   
        - click in the scene picker & select your scene

        ![select scene](./docs/blender_addon_add_scene.png)

        - click on the "+" icon

        ![select scene2](./docs/blender_addon_add_scene2.png)

        - your scene is added to the list
        
        ![select scene3](./docs/blender_addon_add_scene3.png) 

    - export blueprints: check this if you want to automatically export blueprints (default: True)
    - blueprints path: the path to export blueprints to , relative to the main **export folder** (default: library)
    - collection instances: select which option you want to use to deal with collection instances (aka combine mode) (both inside blueprint collections & main collections)

        * split (default, highly recomended) : the addon will 'split out' any nested collections/ blueprints & export them
        * embed: choose this option if you want to keep everything inside a gltf file (less efficient, not recomended)
        * embedExternal: this will embed ONLY collection instances whose collections have not been found inside the current blend file

        These options can also be **overridden** on a per collection instance basis: (if you want to split out most collection instances, but keep a few specific ones embeded
        inside your gltf file)
            
        ![combine override](./docs/combine_override.png) 

        - simply add a custom property called **_combine** to the collection instance, and set it to one of the options above

        please read the dedicated [section](#collection-instances--nested-blueprints) below for more information


    - Export dynamic and static objects seperatly : For MAIN scenes only (aka levels), toggle this to generate 2 files per level: 

        - one with all dynamic data: collection or instances marked as dynamic (aka saveable)
        - one with all static data: anything else that is NOT marked as dynamic, the file name will have the suffix **_dynamic**

        Ie if you add a "Dynamic" custom property/ component to either your collection instances or your blueprint, you get a clean seperation between 

        - your static level data (anything that will never change during the lifetime of your Bevy app)
        - your dynamic objects (anything that will change during the lifetime of your Bevy app, that can be saved & reloaded in save files for example)

    - export materials library: check this if you want to automatically export material libraries (default: False)
    please read the dedicated [section](#materials) below for more information

        > This only works together with blueprints !

    - materials path: where to export materials to

* and your standard gltf export parameters in the **gltf** panel

    ![blender addon use2](./docs/blender_addon_use2.png)


* click on "apply settings"
* now next time you save your blend file you will get an automatically exported gltf file (or more than one, depending on your settings, see below)

### Blueprints

You can enable this option to automatically replace all the **collection instances** inside your main scene with blueprints
- whenever you change your main scene (or your library scene , if that option is enabled), all your collection instances 
    * will be replaced with empties (this will not be visible to you)
    * those empties will have additional custom properties / components : ```BlueprintInfo``` & ```SpawnBlueprint```
    * your main scene/ level will be exported to a much more trimmed down gltf file (see next point)
    * all the original collections (that you used to create the instances) will be exported as **seperate gltf files** into the "library" folder

- this means you will have 
    * one small main gltf file (your level/world)
    * as many gltf files as you have used collections in the main scene , in the library path you specified :
    for the included [basic](../../examples/bevy_gltf_blueprints/basic/) example's [assets](../../examples/bevy_gltf_blueprints/basic/assets/), it looks something like this: 

    ![library](./docs/exported_library_files.png)
    
    the .blend file that they are generated from can be found [here](../../examples/bevy_gltf_blueprints/basic/assets/advanced.blend)

- the above only applies to collections that have **instances** in your main scene!
    if you want a specific collection in your library to always get exported regardless of its use, you need to add 
    a **COLLECTION** (boolean) custom property called ```AutoExport``` set to true
    > not at the object level ! the collection level !

    ![force-export](./docs/force_export.jpg)

    It will get automatically exported like any of the "in-use" collections.

- you can also get an overview of all the exported collections in the export menu

    ![exported collections](./docs/exported_collections.png)

- there are some workflow specificities for multi blend file [workflows](#multiple-blend-file-workflow)

#### Collection instances & Nested blueprints

To maximise reuse of meshes/components etc, you can also nest ***collections instances*** inside collections (as normally in Blender), but also export each nested Blueprint as a seperate blueprints.

> Don't forget to choose the relevant option in the exporter settings (aka **"split"**)

> This replaces the previous "export nested blueprints" checkbox/ option

![instance combine mode](./docs/blender_addon_use4.png)


- To make things clearer: 

    ![nested-blueprints](./docs/nested_blueprints.png)

    - **Player2** & **Enemy** both use the **Humanoid_cactus** nested collection/blueprint, so **Humanoid_cactus** gets exported as a Blueprint for re-use ...but
    - **Humanoid_cactus** is also made up of a main mesh & two instances of **Hand** , so **Hand** gets exported as a Blueprint for re-use ...but
    - **Hand** is also made up of a main mesh & three instances of **Finger**, so **Finger** gets exported as a Blueprint for re-use

- The exported models in this case end up being:

    ![nested_blueprints2](./docs/nested_blueprints2.png)

    - Note how **Player2.glb** is tiny, because most of its data is actually sotred in **Humanoid_cactus.glb**
    - **Enemy.glb** is slightly bigger because that blueprints contains additional meshes
    - All the intermediary blueprints got exported automatically, and all instances have been replaced with "empties" (see explanation in the **Process section** ) to minimize file size

- Compare this to the output **WITHOUT** the nested export option:

    ![nested_blueprints3](./docs/nested_blueprints3.png)

    - less blueprints as the sub collections that are not in use somewhere directly are not exported
    - **Player2.glb** & **Enemy.glb** are significantly larger


TLDR: smaller, more reuseable blueprints which can share sub-parts with other entities !






### Create components from custom properties

- IF you have a valid component type  and the correct corresponding RON string in the custom_property value (this button will not appear if not), this add-on can automatically
generate the corresponding component for you:

- Fill/check your custom property (here for Aabb) 

![generate_components 2](./docs/generate_components2.png)

- click on the button

![generate_components](./docs/generate_components.png)

-voila !

![generate_components 3](./docs/generate_components3.png)







## Use


### Existing components & custom properties

* If you already have components defined manualy in Blender inside **custom properties** you will need to define them again using the UI!
* avoid mixing & matching: if you change the values of **custom properties** that also have a component, the custom property will be **overriden** every time
you change the component's value
* you can of course still use non component custom properties as always, this add-on will only impact those that have corresponding Bevy components







  

## Advanced Tools

In this section you will find various additional more advanced tooling

### Invalid/unregistered type renaming / conversion

If you have components that are
  * invalid : ie some error was diagnosed
  * unregistered: a custom property is present on the object, but there is no matching type in the registry

Here you will get an overview, of ALL invalid and unregistered components in your Blender project, so you can find them, rename/convert them,
or delete them, also in bulk

![component rename overview](./docs/component_rename_overview2.png)

* you can click on the button to select the object in your outliner (this also works across scenes, so you will be taken to the scene where the
given object is located)

![update custom properties](./docs/component_rename_object_select.png)


#### Single object component renaming/ conversion

  - to rename/convert a single component for a single object:
    
    * go to the row of the object you want to convert the component of
    * in the dropdown menu, choose the target component
    * click on the button with the magic wand to convert the component

       ![single rename](./docs/component_rename_single.png)

  > the tool will attempt to automatically convert the source component, including the field names/values, if the target component has the same ones
    If it fails to do the conversion, you will get an error message, and you will either have to change the custom property yourself, or you can simply
    change the values in the UI, which will automatically generate the custom property value

  - to delete a single component for a single object:

    * go to the row of the object you want to remove the component from
    * click on the button with the "x" to remove the component  

       ![single delete](./docs/component_remove_single.png)

#### Bulk component renaming/ conversion

  - use this method if you want to convert ALL components of a given type of ALL objects 

    * click on this button to pick your source component

      ![bulk convert remove](./docs/component_rename_remove_bulk.png)

    * for conversion: in the dropdown menu, choose the target component & click apply to convert all matching components
    * for deletion: clic on the "x" to remove all matching components

      ![bulk convert remove](./docs/component_rename_remove_bulk2.png)


 ### For conversion between custom properties & components & vice-versa

 #### regenerate custom property values

  - "update custom properties of current object" : will go over **all components** that you have defined for the **currently selected object**, and re-generate the 

    corresponding custom property values 

     ![update custom properties](./docs/other_options.png)


  - "update custom properties of ALL objects" : same as above but it will do so for the **ALL objects in your blend file** (so can be slow!), and re-generate the 

    corresponding custom property values 

     ![update custom properties for all](./docs/other_options2.png)

     > IMPORTANT !! use this if you have previously used v0.1 or v0.2 , as v0.3 had a breaking change, that makes it **necessary** to use this **once** to upgrade components data
     You should also re-export your gltf files , otherwise you might run into issues

  
  #### regenerate component/ UI values

   - since v0.2, you have the option to regenerate (for the selected object or all objects, as above) to regenerate your UI values from the custom property values

   ![update UI FROM custom properties](./docs/update_ui_from_custom_properties.png)

   > IMPORTANT !! use this if you have previously used v0.1 , as v0.2 had a breaking change, that makes it **necessary** to use this **once** to upgrade the UI data




## Examples

you can find an example [here](https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/bevy_registry_export/)

