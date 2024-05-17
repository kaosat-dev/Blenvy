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


- move out some parameters from auto export to a higher level (as they are now used in multiple places)
    - [x] main/ library scene names
    - [x] paths

Data storage:
    - for scenes (main scenes)
        - at scene level
    - for blueprints 
        - at collection level
        - Note: these should be COPIED to the scene level when exporting, into the temp_scene's properties

    > NOTE: UP until we manage to create a PR for Bevy to directly support the scene level gltf_extras, the auto exporter should automatically create (& remove)
        an additional object with scene_<scene_name>_components to copy that data to

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
        - [] the assets of local blueprints 


Blueprints:
    - [x] on save: write IN THE COLLECTION PROPERTIES
        - list of assets
        - export path
    - [ ] blueprint selection for nested blueprints is broken

    - [ ] scan & inject on load
    - [ ] scan & inject on save
    - [ ] decide where & when to do & store blueprints data

General things to solve:
 - [x] save settings
 - [x] load settings
    - [ ] add_blueprints_data

- [ ] rename all path stuff using the old naming convention : "export_blueprints_path_full"
- [ ] generate the full paths directly when setting them in the UI  
    - [ ] problem : how to deal with defaults: do it on start/load ?

General issues:
 - there is no safeguard for naming collisions for naming across blender files
 - this can cause an issue for assets list "parent" 
 - "parents" can only be blueprints
    - they normally need/have unique export paths (otherwise, user error, perhaps show it ?)
    - perhaps a simple hashing of the parent's path would be enought 