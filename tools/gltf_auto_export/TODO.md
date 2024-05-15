- investigate remove_blueprints_list_from_main_scene (could be a case of changes to bpy.data not being applied immediatly)
- investigate clearing of changed_objects_per_scene
- it seems bevy_components does not trigger updates
- undo redo is ignored: ie save, do something, undo it, you still get changes


- [ ] serialize scene
   - [ ] for collection instances: 
      * [ ] blueprints export should also take the split/embed mode into account: if a nested collection changes AND embed is active, its container collection should also be exported
      * [ ] level exports should do the same
   - [ ] add tests for the above
   - [ ] look into caching for serialize scene
   - [ ] replace field name based logic with type base logic 

- [ ] to make things easier overall we need a mapping of Blueprints/Collections to
   - [x] their instances
   - [x] their objects/sub collections instances etc
   - [ ] a mapping of objects to the blueprints they belong to
- [ ] things to alter/remove using the new & improved Blueprints/collections scanning and mapping
   - [x] get_sub_collections                          => remove , but rewrite how BlueprintsList are generated
   - [x] get_used_collections                         => remove , but rewrite how BlueprintsList are generated
   - [x] get_exportable_collections                   => remove , but replace with new function to get exportable blueprints
   - [x] get_collections_per_scene
   - [x] get_collections_in_library
   - [ ] traverse_tree                                => keep, used
   - [x] find_layer_collection_recursive              => remove, unused
   - [ ] recurLayerCollection                         => unclear, analyse
   - [x] find_collection_ascendant_target_collection  => remove, double check
   - [x] set_active_collection                        => keep, used
   - [x] get_source_scene                             => remove, unused 
   - [x] assets_list["BlueprintsList"]
      BLUEPRINTS LIST {'Blueprint1': [], 'Blueprint6_animated': [], 'Blueprint4_nested': ['Blueprint3'], 'Blueprint3': [], 'Blueprint7_hierarchy': [], 'External_blueprint': [], 'External_blueprint2': ['External_blueprint3'], 'External_blueprint3': [], 'Blueprint8_animated_no_bones': []}
   - [x] internal_collections => replace with "internal_collections" or "local_collections"
   
- [x] fix COMBINE MODE passed as int instead of enum value
   => comes from our custom logic for add_on prefs
- [ ] double check compares to "None" values

- [ ] add tests for relative/absolute paths

- [x] move all things that alter data "permanently" to pre-save
   - [x] lighting/ scene components injection
   - [x] blueprintNames ?
   - [x] or more simple: just remove them after save as we do for others: lighting_components

   - [ ] if we want the blueprintsList / future paths of blueprints to be present inside external assets, we are going to need to keep them around, ie: inject them in pre-save & not remove them 

- [ ] update cleanup_materials

- [x] remove legacy mode
   - [x] from auto_export
   - [x] from rust code
   - [x] from examples
   - [x] added notes & workaround information in docs

- [ ] remove bulk of tracker related code
- [ ] clean up
- [x] split up change detection in settings to its own panel




Change storage of 'blueprint' assets : (from BlueprintsList)
 - store at the SCENE level: a list/map of assets 
   - asset name + asset path
   - the asset PATH is determined by the export output folder parameters
   - make asset storage generic enough to allow adding additional asset types
   - get inspired by bevy_asset_loader ?

