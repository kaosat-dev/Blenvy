Basics
- [x] add panel
- [x] add a "create blueprint" button
    - [x] when clicked: 
        - [x] create collection 
        - [x] add an empty inside collection and name it <COLLECTION_NAME>_components
        - [x] add a **AutoExport** Boolean property to collection 
        - [x] add name imput(popup for name input ?)

- [x] add a list of existing components/custom properties
- [x] add an "edit blueprint" section
    - [x] only filled when there is ONE selection, and that selection is a collection
    - [x] add a dropdown of possible components  
    - [x] add a checkbox for enabling disabling a component (enabled by default)
    - [x] add a button for copying a component
    - [x] add a button for pasting a component


UI:
 - [x] filterable list of components to DISPLAY for selection : ComponentDefinitionsList

- Filter out invalid objects for components that have no _components suffix ? (that is too limiting I think)
- -[x] How to deal with pre-existing custom properties that have NO metadata
    * if there is one without metadata: find if there is an available component with the same name & type ?
    * if there is , insert metadata
    * otherwise, mark it in some way visually ?

- [x] for OBJECT enums: add two ui pieces
    - [x] one for selecting the TYPE to choose (ie normal enum)
    - [x] one for setting the VALUE inside that


- [x] vecs => (not vec2, vec3 etc) more complex UI to add items in a list
    - [x] generate contained CollectionGroup
    - [x] CollectionProperty => type = the above
- [x] find ways to "collapse" the different levels of nested data of structs/tupples into a single custom property (ideally on the fly, but we can do without)

- [x] for single tupple components that represent a single unit type, re_use the base type's UIPropertyGroup instead of creating specific ones (ie TuppleTestF32_ui...) => will not work, would cause overriden "update callback"
- [x] pre_generate default values/values for each main type

- [x] fix issues with vec2 etc not having the correct number of items
- [x] fix bad defaults in ui group
- [x] fix object enums handling on updates (??)
- [x] fix issues with lambads in loops

- [x] object enum should be <EntryName>(params)
    ie  *Collider:
            * Cuboid(Vec3)
            * Sphere(radius)
- [x] deal with enums variants that do not have any data: ex   {
          "title": "Mesh"
        }

- [x] remove / change use of ComponentDefinitionsList 
    - when filling the list, use the long_name as index ie items.append((str(index), item.name, item.long_name)) => items.append((item.long_name, item.name, item.long_name))
- [x] when removing a component, reset the value of the attribute in the property group (or not ? could be a feature)
- [x] deal correctly with fields of types that are NOT in the schema.json (for ex PlayingAnimation in AnimationPlayer)
- [ ] deal correctly with complex types 
            CascadeShadowConfig: has an array/list
            ClusterConfig: one of the enum variants is an object
- [ ] possibly allow Color to be an enum as it should be ?
- [x] for sub items , the update functions "Name" should be the one of the root object
- [x] fix copy & pasting
    - it actually works, but the value of the custom property are not copied back to the UI, need to implement property_group_value_from_custom_property_value
- [ ] we need a notion of "root propertyGroup" =?
- [x] notify user of missing entries in schema (ie , unregistered data types)
- [x] clarify propgroup_ui vs named nested fields
- [x] fix basic enums handling
- [x] add a list of not found components to the registry, add to them on the fly
- [x] add configuration panel (open the first time, closed on further user once configured)

- [ ] only upgrade custom properties to metadata when asked/relevant
- [x] add limits to ixxx types vs utypes
- [x] only display the "generate components xx" when relevant ie:
    - go through list of custom properties in current object
        - if one does not have metadata and / or propgroup: 
            break 

- [x] remove custom property of disabled component ? => NOpe, as we need custom properties to iterate over
- [x] what to do with components with n/a fields ? perhaps disable the component ? add a "invalid" field to meta ?
- [ ] format output as correct RON
- [ ] change custom property => propGroup to convert RON => Json first
- [ ] cleanup process_lists

bpy.context.window_manager
    .components_registry => raw registry
    .components_list =>  refined, pythonified list of available components


- perhaps directly export default values within the schema.json ?
        - for most types , it is straighforward, but others, not so muc: like the default color in Bevy , etc


# Additional
    - [ ] check if output "string" in custom properties are correct

    - gltf_auto_export
        - [ ] add support for "enabled" flag
        - [ ] add special components 
                - "AutoExport" => Needed
                - "Dynamic" ? naah wait that should be exported by the Bevy side
        - [ ] filter out Components_meta ??
    - bevy_gltf_components:
        - add "compatibility mode" and deprecation warnings for the current hack-ish conversion of fake ron

    