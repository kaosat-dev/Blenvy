



bpy.context.window_manager
    .components_registry => raw registry
    .components_list =>  refined, pythonified list of available components


- perhaps directly export default values within the schema.json ?
        - for most types , it is straighforward, but others, not so muc: like the default color in Bevy , etc

UI:
 - [x] filterable list of components to DISPLAY for selection : ComponentDefinitionsList

- Filter out invalid objects for components that have no _components suffix
- -[x] How to deal with pre-existing custom properties that have NO metadata
    * if there is one without metadata: find if there is an available component with the same name & type ?
    * if there is , insert metadata
    * otherwise, mark it in some way visually ?

- [ ] for OBJECT enums: add two ui pieces
    - [ ] one for selecting the TYPE to choose (ie normal enum)
    - [ ] one for setting the VALUE inside that


- [ ] vecs => (not vec2, vec3 etc) more complex UI to add items in a list
- [ ] find ways to "collapse" the different levels of nested data of structs/tupples into a single custom property (ideally on the fly, but we can do without)

- [ ] for single tupple components that represent a single unit type, re_use the base type's UIPropertyGroup instead of creating specific ones (ie TuppleTestF32_ui...)
- [ ] pre_generate default values/values for each main type

- [x] fix issues with vec2 etc not having the correct number of items
- [ ] fix bad defaults in ui group
- [ ] fix object enums handling on updates (??)
- [x] fix issues with lambads in loops

- [x] object enum should be <EntryName>(params)
    ie  *Collider:
            * Cuboid(Vec3)
            * Sphere(radius)

- [] remove / change use of ComponentDefinitionsList 
    - when filling the list, use the long_name as index ie items.append((str(index), item.name, item.long_name)) => items.append((item.long_name, item.name, item.long_name))
- [ ] when removing a component, reset the value of the attribute in the property group (or not ? could be a feature)
- [ ] deal correctly with fields of types that are NOT in the schema.json (for ex PlayingAnimation in AnimationPlayer)