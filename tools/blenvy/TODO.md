Auto export
 - [x] the original blueprints & levels path are now left as is, and there is an auto injection of xxxpath_full for absolute paths
    - [x] replace all uses of the paths with the correct ones above
        - [x] levels
        - [x] blueprints
        - [x] materials
 - [x] move out the UI for "assets" folder out of "blueprints condition"
 - [x] fix asset path calculations
     - root path => relative to blend file path
     - asset path => relative to root path
     - blueprints/levels/blueprints path => relative to assets path
 - [ ] add error handling for de/serialization of project, so that in case of error, the previous saved serialized project is thrown away

- move out some parameters from auto export to a higher level (as they are now used in multiple places)
    - [x] main/ library scene names
    - [x] paths

- [ ] Data storage for custom properties:
    - for scenes (main scenes)
        - at scene level
    - for blueprints 
        - at collection level
        - Note: these should be COPIED to the scene level when exporting, into the temp_scene's properties

    > NOTE: UP until we manage to create a PR for Bevy to directly support the scene level gltf_extras, the auto exporter should automatically create (& remove)
        any additional object with scene_<scene_name>_components to copy that data to

Assets:
    - blueprint assets should be auto_generated & inserted into the list of assets : these assets are NOT removable by the user
    - should not change the list of manually added assets
 - [x] store assets 
   - [x] per main scene for level/world assets
   - [x] per blueprint for blueprint in lib scene
 - [ ] UI:
    - [x] we need to display all direct assets (stored in the scene)
    - [ ] indirect assets: 
        - QUESTION : do we want to include them in the list of assets per level ? 
            -  this would enable pre-loading ALL the assets, but is not ideal in most other cases
            - so add an option ?
        - [ ] the assets of local blueprints 

Blueprints:
    - [x] on save: write IN THE COLLECTION PROPERTIES
        - list of assets
        - export path
    - [ ] blueprint selection for nested blueprints is broken

    - [ ] scan & inject on load
    - [ ] scan & inject on save
    - [ ] decide where & when to do & store blueprints data

Components:
    - [x] add support for adding components to collections
    - [ ] upgrade all operators:
        - [x] add 
        - [x] remove
        - [x] copy & paste
        - [ ] OT_rename_component
        - [ ] Fix_Component_Operator
    - [ ] add handling for core::ops::Range<f32> & other ranges
    - [ ] fix is_component_valid that is used in gltf_auto_export
    - Hashmap Support
        - [x] fix parsing of keys's type either on Bevy side (prefered) or on the Blender side 
        - [x] fix weird issue with missing "0" property when adding new entry in empty hashmap => happens only if the values for the "setter" have never been set
        - [ ] handle missing types in registry for keys & values

    - [ ] Add correct upgrade handling from individual component to bevy_components
    - [x] Settings handling:
        - [x] move saveable settings out to a settings file
        - [x] update save & load
        - [x] add handling of polling frequency & enabling


General things to solve:
 - [x] save settings
 - [x] load settings
    - [x] add blueprints data

- [x] rename all path stuff using the old naming convention : "blueprints_path_full"
- [x] generate the full paths directly when setting them in the UI  
    - [x] problem : how to deal with defaults: do it on start/load ?
- [x] filter out scenes that have already been used in scenes list

General issues:
 - there is no safeguard for naming collisions for naming across blender files
 - this can cause an issue for assets list "parent" 
 - "parents" can only be blueprints
    - they normally need/have unique export paths (otherwise, user error, perhaps show it ?)
    - perhaps a simple hashing of the parent's path would be enought 


 - [x] addon-prefs => settings
 - [x] generate_gltf_export_settings => should not use add-on prefs at all ? since we are not overriding gltf settings that way anymore ?
 - [x] remove hard coded path for standard gltf settings
 - [x] load settings on file load
    - [x] auto_export
    - [x] components
    - [ ] add handling of errors when trying to load settings


- [ ] force overwrite of settings files instead of partial updates ?
- [ ] add tests for disabled components 
- [x] fix auto export workflow
- [ ] should we write the previous _xxx data only AFTER a sucessfull export only ?
- [x] add hashing of modifiers/ geometry nodes in serialize scene
- [x] add ability to FORCE export specific blueprints & levels
- [ ] undo after a save removes any saved "serialized scene" data ? DIG into this
- [ ] handle scene renames between saves (breaks diffing)
- [x] change scene selector to work on actual scenes aka to deal with renamed scenes
    - [x] remove get_main_and_library_scenes as it should not be needed anymore
- [x] fix asset file selection
- [x] change "assets" tab to "levels"/worlds tab & modify UI accordingly
- [ ] add option to 'split out' meshes from blueprints ? 
    - [ ] ie considering meshletts etc , it would make sense to keep blueprints seperate from purely mesh gltfs

- [ ] remove 'export_marked_assets' it should be a default setting
- [x] disable/ hide asset editing ui for external assets
- [ ] inject_export_path_into_internal_blueprints should be called on every asset/blueprint scan !! Not just on export
- [ ] fix level asets UI 

clear && pytest -svv --blender-template ../../testing/bevy_example/art/testing_library.blend --blender-executable /home/ckaos/tools/blender/blender-4.1.0-linux-x64/blender tests/test_bevy_integration_prepare.py  && pytest -svv --blender-executable /home/ckaos/tools/blender/blender-4.1.0-linux-x64/blender tests/test_bevy_integration.py