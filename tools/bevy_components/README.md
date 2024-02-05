# Bevy components

This [Blender addon](./)  gives you an easy to use UI to add and configure your [Bevy]() components inside Blender !
- **automatically generates a simple UI** to add/configure components based on a **schema** file (an export of all your Bevy components)
- no more need to specify components manually using custom_properties, with error prone naming etc
- adds **metadata** to objects containing information about what components it uses
- adds the ability to **toggle components** on/off without having to remove the component from the object
- can **convert** existing custom properties to "upgraded" ones containing metadata
- uses Blender's **PropertyGroups** to generate custom UIs & connects those groups with the custom properties so that no matter the complexity
of your Bevy components you get a nicely packed custom_property to use with ...
- the ideal companion to the [gltf_auto_export]() to embed your Bevy components inside your gltf files

> Important: 
  the tooling is still in the early stages, even if it is close to feature complete : I advise keeping a backup of your blend file around.

## Installation: 

* grab the latest release zip file

![blender addon install](./docs/blender_addon_install_zip.png)


* in Blender go to edit =>  preferences => install

![blender addon install](./docs/blender_addon_install.png)

* choose the path where ```bevy_components.zip``` is stored

![blender addon install](./docs/blender_addon_install2.png)


## Useage

- "generate components from custom properties" :
   - if you have existing compatible custom properties without metadata (ie custom properties that match a type name in the schema file), this button will be displayed
   - once you click on it, component metadata (+ui property groups) will be generated for all compatible components
   - this operator will attempt to fill in the data correctly, and if not possible will give you the default component values


## License

This tool, all its code, contents & assets is Dual-licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](../LICENSE_APACHE.md) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](../LICENSE_MIT.md) or https://opensource.org/licenses/MIT)