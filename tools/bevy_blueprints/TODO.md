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


- [ ] vecs => (not vec2, vec3 etc) more complex UI to add items in a list
    - [ ] generate contained CollectionGroup
    - [ ] CollectionProperty => type = the above
- [x] find ways to "collapse" the different levels of nested data of structs/tupples into a single custom property (ideally on the fly, but we can do without)

- [ ] for single tupple components that represent a single unit type, re_use the base type's UIPropertyGroup instead of creating specific ones (ie TuppleTestF32_ui...)
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
- [ ] when removing a component, reset the value of the attribute in the property group (or not ? could be a feature)
- [x] deal correctly with fields of types that are NOT in the schema.json (for ex PlayingAnimation in AnimationPlayer)
- [ ] deal correctly with complex types 
            CascadeShadowConfig: has an array/list
            ClusterConfig: one of the enum variants is an object
- [ ] possibly allow Color to be an enum as it should be ?
- [x] for sub items , the update functions "Name" should be the one of the root object
- [x] fix copy & pasting
    - it actually works, but the value of the custom property are not copied back to the UI, need to implement property_group_value_from_custom_property_value
- [ ] we need a notion of "root propertyGroup" =?

# Additional
    - [ ] check if output "string" in custom properties are correct
    - update gltf_auto_export to take into account component metadata ? (might not be needed, except for "enabled" flag)