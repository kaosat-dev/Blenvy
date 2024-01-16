



bpy.context.window_manager
    .components_registry => raw registry
    .components_list =>  refined, pythonified list of available components


- perhaps directly export default values within the schema.json ?
        - for most types , it is straighforward, but others, not so muc: like the default color in Bevy , etc

UI:
 - [x] filterable list of components to DISPLAY for selection : ComponentDefinitionsList

- Filter out invalid objects for components that have no _components suffix
- -[ ] How to deal with pre-existing custom properties that have NO metadata
    * if there is one without metadata: find if there is an available component with the same name & type ?
    * if there is , insert metadata
    * otherwise, mark it in some way visually ?

- [ ]