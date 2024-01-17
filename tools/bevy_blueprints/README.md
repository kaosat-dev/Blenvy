



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