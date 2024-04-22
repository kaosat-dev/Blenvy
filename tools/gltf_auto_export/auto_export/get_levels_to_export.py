import bpy
from ..helpers.helpers_blueprints import check_if_blueprint_on_disk
from ..helpers.helpers_scenes import (get_scenes, )

# IF collection_instances_combine_mode is not 'split' check for each scene if any object in changes_per_scene has an instance in the scene
def changed_object_in_scene(scene_name, changes_per_scene, blueprints_data, collection_instances_combine_mode):
    # Embed / EmbedExternal
    if collection_instances_combine_mode == 0: # 1 => Embed
        return False

    blueprints_from_objects = blueprints_data.blueprints_from_objects

    bluprint_instances_in_scene = blueprints_data.blueprint_instances_per_main_scene[scene_name]
    changed_objects = [object_name for change in changes_per_scene.values() for object_name in change.keys()] 
    changed_blueprints = [blueprints_from_objects[changed] for changed in changed_objects if changed in blueprints_from_objects]
    changed_blueprints_with_instances_in_scene = [bla for bla in changed_blueprints if bla.name in bluprint_instances_in_scene]#[blueprints_from_objects[changed] for changed in changed_objects if changed in blueprints_from_objects and changed in bluprint_instances_in_scene]
    
    level_needs_export = len(changed_blueprints_with_instances_in_scene) > 0
    print("changed_blueprints", changed_blueprints)
    print("bluprint_instances_in_scene", bluprint_instances_in_scene, "changed_objects", changed_objects, "changed_blueprints_with_instances_in_scene", changed_blueprints_with_instances_in_scene)

    return level_needs_export


# this also takes the split/embed mode into account: if a collection instance changes AND embed is active, its container level/world should also be exported
def get_levels_to_export(changes_per_scene, changed_export_parameters, blueprints_data, addon_prefs):
    export_change_detection = getattr(addon_prefs, "export_change_detection")
    export_gltf_extension = getattr(addon_prefs, "export_gltf_extension")
    export_models_path = getattr(addon_prefs, "export_models_path")
    collection_instances_combine_mode = getattr(addon_prefs, "collection_instances_combine_mode")

    [main_scene_names, level_scenes, library_scene_names, library_scenes] = get_scenes(addon_prefs)
 
    # determine list of main scenes to export
    # we have more relaxed rules to determine if the main scenes have changed : any change is ok, (allows easier handling of changes, render settings etc)
    main_scenes_to_export = [scene_name for scene_name in main_scene_names if not export_change_detection or changed_export_parameters or scene_name in changes_per_scene.keys() or changed_object_in_scene(scene_name, changes_per_scene, blueprints_data, collection_instances_combine_mode) or not check_if_blueprint_on_disk(scene_name, export_models_path, export_gltf_extension) ]

    print("main_scenes_to_export", main_scenes_to_export, changes_per_scene)
    return (main_scenes_to_export)