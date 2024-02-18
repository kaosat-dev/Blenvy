# Bevy components

This [Blender addon](https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/tools/bevy_components)  gives you an easy to use UI to add and configure your [Bevy](https://bevyengine.org/) components inside Blender !

- **automatically generates a simple UI** to add/configure components based on a **registry schema** file (an export of all your Bevy components's information, generated)
by the [bevy_registry_export](https://crates.io/crates/bevy_registry_export) crate/plugin
- no more need to specify components manually using custom_properties, with error prone naming etc
- adds **metadata** to objects containing information about what components it uses + some extra information
- uses Blender's **PropertyGroups** to generate custom UIs & connects those groups with the custom properties so that no matter the complexity
of your Bevy components you get a nicely packed custom_property to use with ...
- the ideal companion to the [gltf_auto_export](https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/tools/gltf_auto_export) to embed your Bevy components inside your gltf files
<!-- - adds the ability to **toggle components** on/off without having to remove the component from the object -->


> Important: 
  the tooling is still in the early stages, even if it is feature complete : use with caution!.

> IMPORTANT !! if you have previously used v0.1 , v0.2 had a breaking change, please see [this](#regenerate-ui-values) section on how to upgrade your data to v0.2.\
This problem should not be present going forward

## Installation: 

* grab the latest release zip file from the releases tab (choose the bevy_components releases !)

<!--![blender addon install](./docs/blender_addon_install_zip.png)-->

* in Blender go to edit =>  preferences => install

![blender addon install](./docs/blender_addon_install.png)

* choose the path where ```bevy_components.zip``` is stored

![blender addon install](./docs/blender_addon_install2.png)


## Configuration & overview

Before you can use the add-on you need to configure it

### Bevy side

 - setup [bevy_registry_export](https://crates.io/crates/bevy_registry_export) for your project (see the crate's documentation for that), and compile/run it to get the ```registry.json``` file

### Blender side

- Go to the new Bevy Components tab in the 3D view

![configuration](./docs/configuration.png)

- click on the button to select your registry.json file (in the "configuration" panel)

![configuration 2](./docs/configuration2.png)

- the list of available components will appear

![configuration 3](./docs/configuration3.png)



## Use


### Existing components & custom properties

* If you already have components defined manualy in Blender inside **custom properties** you will need to define them again using the UI!
* avoid mixing & matching: if you change the values of **custom properties** that also have a component, the custom property will be **overriden** every time
you change the component's value
* you can of course still use non component custom properties as always, this add-on will only impact those that have corresponding Bevy components

### adding components

- to add a component, select an object and then select the component from the components list: (the full type information will be displayed as tooltip)

![components list](./docs/components_list.png)

- click on the dropdown to get the full list of available components

![components list](./docs/components_list2.png)

- you can also filter components by name for convenience

![filter components](./docs/filter_components.png)


- add a component by clicking on the "add component" button once you have selected your desired component
  
  it will appear in the component list for that object

![add component](./docs/add_component.png)

### edit components

- to edit a component's value just use the UI: 

![edit component](./docs/edit_component.png)

it will automatically update the value of the corresponding custom property

![edit component](./docs/edit_component2.png)

### Create components from custom properties

- IF you have a valid component type  and the correct corresponding RON string in the custom_property value (this button will not appear if not), this add-on can automatically
generate the corresponding component for you:

- Fill/check your custom property (here for Aabb) 

![generate_components 2](./docs/generate_components2.png)

- click on the button

![generate_components](./docs/generate_components.png)

-voila !

![generate_components 3](./docs/generate_components3.png)


### copy & pasting 

- you can also copy & paste components between objects

- click on the "copy component button" of the component you want to copy

![copy component](./docs/copy_component.png)

- then select the object you want to copy the component (& its value) to, and click on the paste button.

It will add the component to the select object

![paste component](./docs/paste_component.png)

> if the target object already has the same component, its values will be overwritten


## Additional components UI features

- for large/ complex components you can toggle the details of that component:

![toggle details](./docs/toggle_details.png)


## Supported components

- normally (minus any bugs, please report those!) all components using **registered** types should be useable and editable
- this includes (non exhaustive list):
  * enums (even complex ones !)

    ![enums](./docs/enums.png)

    ![enums](./docs/enums2.png)

  
  * complex structs, with various types of fields (including nested ones)

    ![complex](./docs/complex_components2.png)

  * lists/ vecs (here a vec of tuples)

    ![lists](./docs/vecs_lists.png)

  * etc !

## Unregistered types & error handling

- non registered types can be viewed in this panel : (can be practical to see if you have any missing registrations too!)

    ![unregistered types](./docs/unregistered_types.png)

- if you have a component made up of unregistered structs/enums etc, you will get visual feedback & the component will be deactivated

    ![invalid component](./docs/invalid_components.png)

    > important ! ```gltf_auto_export``` currently has no way of filtering out components, so you need to delete invalid components like these before exporting
    this will be adress in the future

- if you are encountering this type of view: don't panic your component data is not gone ! It just means you need to reload the registry data by clicking on the relevant button

    ![missing registry data](./docs/missing_registry_data.png)

  

## advanced configuration

 ### registry file polling


  * by default, the add-on will check for changes in your registry file every second, and refresh the UI accordingly
    * you can set the polling frequency or turn it off if you do not want auto-refresh

    ![registry file polling](./docs/registry_polling.png)


 ### regenerate custom property values

  - "update custom properties of current object" : will go over **all components** that you have defined for the **currently selected object**, and re-generate the 

    corresponding custom property values 

     ![update custom properties](./docs/other_options.png)


  - "update custom properties of ALL objects" : same as above but it will do so for the **ALL objects in your blend file** (so can be slow!), and re-generate the 

    corresponding custom property values 

     ![update custom properties for all](./docs/other_options2.png)

  
  ### regenerate UI values

   - since v0.2, you have the option to regenerate (for the selected object or all objects, as above) to regenerate your UI values from the custom property values

   ![update UI FROM custom properties](./docs/update_ui_from_custom_properties.png)

   > IMPORTANT !! use this if you have previously used v0.1 , as v0.2 had a breaking change, that makes it **necessary** to use this **once** to upgrade the UI data


## Additional important information


- for the components to work correctly with [```bevy_gltf_components```](https://crates.io/crates/bevy_gltf_components) or [```bevy_gltf_blueprints```](https://crates.io/crates/bevy_gltf_blueprints) you will need to set the ```legacy_mode``` for those plugins to **FALSE**
as the component data generated by this add on is a complete, clean **ron** data that is incompatible with the previous (legacy versions).
Please see the documentation of those crates for more information.

> Note: the legacy mode support will be dropped in future versions, and the default behaviour will be NO legacy mode


## Examples

you can find an example [here](https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/bevy_registry_export/)

## Known issues & limitations:

* **Range** data (ie ```Range<f32>``` etc) are not handled at this time (issue seems to be on the Bevy side)
* **Entity** structs are always set to 0 (setting entity values on the Blender side at this time does not make much sense anyway) 

## License

This tool, all its code, contents & assets is Dual-licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](../LICENSE_APACHE.md) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](../LICENSE_MIT.md) or https://opensource.org/licenses/MIT)