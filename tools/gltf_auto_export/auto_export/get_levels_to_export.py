import bpy
from .export_blueprints import check_if_blueprint_on_disk
from ..helpers.helpers_scenes import (get_scenes, )

def changed_object_in_scene(scene_name, changes_per_scene, collections, collection_instances_combine_mode):
    print("BLAAAAAAAAAAAAAAAAAAAAAAAAAAAAH", scene_name, "combo mode", collection_instances_combine_mode, "changes", changes_per_scene, "collections", collections)
    # TODO: IF collection_instances_combine_mode is not 'split' check for each scene if any object in changes_per_scene has an instance in the scene
    # Embed / EmbedExternal
    if collection_instances_combine_mode == 0: # 1 => Embed
        return False
    """if scene_name in list(changes_per_scene.keys()):
        print("here", scene_name)"""


    for scene_name_current in list(bpy.data.scenes.keys()):


        for object in bpy.data.scenes[scene_name_current].objects:
            print("foo", changes_per_scene[scene_name_current])
            if object.instance_type == 'COLLECTION':
                collection_name = object.instance_collection.name

            if object.name in list(changes_per_scene[scene_name_current].keys()):
                print("changed object", object.name)
                return True # even a single object is enough to flag the scene


# TODO: this should also take the split/embed mode into account: if a collection instance changes AND embed is active, its container level/world should also be exported
def get_levels_to_export(changes_per_scene, changed_export_parameters, collections, addon_prefs):
    print("TOTOOO")
    export_change_detection = getattr(addon_prefs, "export_change_detection")
    export_gltf_extension = getattr(addon_prefs, "export_gltf_extension")
    export_models_path = getattr(addon_prefs, "export_models_path")
    collection_instances_combine_mode = getattr(addon_prefs, "collection_instances_combine_mode")

    [main_scene_names, level_scenes, library_scene_names, library_scenes] = get_scenes(addon_prefs)
 
    # print("levels export", "export_change_detection", export_change_detection, "changed_export_parameters",changed_export_parameters, "export_models_path", export_models_path, "export_gltf_extension", export_gltf_extension, "changes_per_scene", changes_per_scene)
    # determine list of main scenes to export
    # we have more relaxed rules to determine if the main scenes have changed : any change is ok, (allows easier handling of changes, render settings etc)
    main_scenes_to_export = [scene_name for scene_name in main_scene_names if not export_change_detection or changed_export_parameters or scene_name in changes_per_scene.keys() or not check_if_blueprint_on_disk(scene_name, export_models_path, export_gltf_extension) or changed_object_in_scene(scene_name, changes_per_scene, collections, collection_instances_combine_mode)]
    return (main_scenes_to_export)