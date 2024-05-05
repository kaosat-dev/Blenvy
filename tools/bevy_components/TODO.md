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
          "long_name": "Mesh"
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

- [x] add limits to ixxx types vs utypes
- [x] only display the "generate components xx" when relevant ie:
    - go through list of custom properties in current object
        - if one does not have metadata and / or propgroup: 
            break 

- [x] remove custom property of disabled component ? => NOpe, as we need custom properties to iterate over
- [x] what to do with components with n/a fields ? perhaps disable the component ? add a "invalid" field to meta ?
- [x] format output as correct RON
    - [x] fix issue with empty strings
- [x] change custom property => propGroup to convert RON => Json first => obsolete
- [x] cleanup process_lists

- [x] fix issues with enum variants with only a long_name

- [x] display single item enums inline, others in a seperate row

- [x] add button to "apply all" (in configuration), to apply/update all custom properties to ALL objects where relevant
- [x] add button to "apply to current" to do the same with current
- [x] add warning sign to the above

- [x] what about metadata ?
- [x] only upgrade custom properties to metadata when asked/relevant
- [x] implement move list up/down
- [ ] change property_group_value_from_custom_property_value => just disregard it for now, its point is very limited (helping people with old custom properties by attempting to generate real values)
    and give the change to a real ron format, it is too limiting
- [x] fix reload registry clearing list of missing types 
- [x] clean up metadata module, a lot of repeated code
- [x] some fields when original is 0 or 0.0 are not copyable ? (seems like a bad boolean check )
- [x] fix issues with object variants in enums (see clusterconfig)


- perhaps directly export default values within the schema.json ?
        - for most types , it is straighforward, but others, not so much: like the default color in Bevy , etc

- [x] change default schema.json to registry.json
- [x] pasted components do not get updated value in custom_property
- [x] finish documentation
- [x] add storage of registry path
    - [x] save after setting the data (browse for)
    - [x] load after each reload ?

# Additional
    - [x] check if output "string" in custom properties are correct

    - gltf_auto_export
        - [x] add support for "enabled" flag
        - [ ] add special components 
                - "AutoExport" => Needed
                - "Dynamic" ? naah wait that should be exported by the Bevy side
        - [x] filter out Components_meta ??
        - [x] add legacy mode to the persisted parameters

    - bevy_gltf_components:
        - [x] first release patch for current issues
        - [x] make configurable 
        - [x] add "compatibility mode" and deprecation warnings for the current hack-ish conversion of fake ron
        - [x] update docs to show we need to use ComponentsFromGltfPlugin::default

    - bevy_gltf_blueprints
        - [x] update dependency
        - [x] update version
        - [x] add ability to set legacy mode for bevy_gltf_components ? 

    - [x] release all versions
    - [x] update main documentation, add compatibility version grid

    
## Phase 2

- [x] fix handling of long component names
    - [x] fix nesting level handling issue for new system : ie basic component DOES NOT work, but nestedLevel2 does
    - add goddam tests !
    - [ ] verify some weird prop => custom property values (Calculated Clip for example)

- [x] fix "reload registry" not clearing all previous data (reloading registry does not seem to account for added/removed components in the registry )
- add file watcher for registry
    - [x] have the watcher work as expected
    - [ ] add handling of removed registry file
    - [ ] clear & reset handler when the file browser for the registry is used
- [ ] re-enable watcher

- tests
    clear && pytest -svv --blender-executable <path_to_blender>/blender/blender-4.0.2-linux-x64/blender

    - [x] load registry
    - just check list of components vs lists in registry
    - [x] try adding all components
        - [x] select an object
        - [x] call the add_component operator 

    - [x] change params 
        - use field names + component definitions to set values
        - [x] find a way to shuffle params of ALL components based on a reliable, repeatable seed

    - [x] test propgroup values => custom property values
    - [x] test custom property value => propgroup value 

    - check if all went well

 - [x] fix issues with incorect custom_property generation
   - [x] fix issue with object variants for enums

 - [ ] add handling for core::ops::Range<f32> & other ranges
 - [x] add handling for alloc::borrow::Cow<str>
 - [x] add handling of isize

 - [x] indirection level
    - currently 
        - short_name +_"ui => direct lookup
        - problem : max 64 chars for propertyGroupNames
    - possible solution
        - propertyGroupName storage: simple , incremented INT (call it propGroupId for ex)
        - lookup shortName => propGroupId

    - do a first pass, by replacing manual propGroupNames creation with a function
    - in a second pass, replace the innards

- add button to regenerate cutom prop values from custom properties (allows us to sidestep any future issues with internals changing)
    - [x] fix lists
    - [x] fix enums (see Clusterconfig)
        - [x] need an example with one tupple one struct
        - [x] projection
        - [x] additionalmassproperties
    - [x] fix tupleStructs (see TupleVecF32F32) =>  always the same problem of having us pre-parse data without knowing what we have inside
        - find a way to only split by level 0 (highest level) nesting "," seperators, ignoring any level of nesting until we dig one level deeper
        - solve nesting level use issues

- [x] remove metadata when deleting components
- [x] add try catch around custom_prop =>  propGroup
- [x] enhance the GenerateComponent_From_custom_property_Operator to use the new system to actually generate the stuff

- coherence in operators: 
    - component_name vs component_type
    - [x] delete => remove

- [x] clean up reloading of registry settings
- [x] clean up file watcher


=========================================
Restructuring of storage of components
- [x] marking of invalid root propgroups/components should be based on long name
- [ ] overhaul & check each prop group type's use of short names => long names
    - [ ] lists

- [ ] in conversions from propgroups
        component_name = definition["short_name"]
- [ ] fix is_component_valid that is used in gltf_auto_export

- Hashmap Support
    - [ ] fix parsing of keys's type either on Bevy side (prefered, unlikely to be possible) or on the Blender side 
    - [ ] handle missing types in registry for keys & values