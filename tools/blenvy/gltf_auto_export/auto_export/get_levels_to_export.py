import bpy
from ...blueprints.blueprint_helpers import check_if_blueprint_on_disk
from ..helpers.helpers_scenes import (get_scenes, )

# IF collection_instances_combine_mode is not 'split' check for each scene if any object in changes_per_scene has an instance in the scene
def changed_object_in_scene(scene_name, changes_per_scene, blueprints_data, collection_instances_combine_mode):
    # Embed / EmbedExternal
    blueprints_from_objects = blueprints_data.blueprints_from_objects

    blueprint_instances_in_scene = blueprints_data.blueprint_instances_per_main_scene.get(scene_name, None)
    if blueprint_instances_in_scene is not None:
        changed_objects = [object_name for change in changes_per_scene.values() for object_name in change.keys()] 
        changed_blueprints = [blueprints_from_objects[changed] for changed in changed_objects if changed in blueprints_from_objects]
        changed_blueprints_with_instances_in_scene = [blueprint for blueprint in changed_blueprints if blueprint.name in blueprint_instances_in_scene.keys()]


        changed_blueprint_instances= [object for blueprint in changed_blueprints_with_instances_in_scene for object in blueprint_instances_in_scene[blueprint.name]]
        # print("changed_blueprint_instances", changed_blueprint_instances,)

        level_needs_export = False
        for blueprint_instance in changed_blueprint_instances:
            blueprint = blueprints_data.blueprint_name_from_instances[blueprint_instance]
            combine_mode = blueprint_instance['_combine'] if '_combine' in blueprint_instance else collection_instances_combine_mode
            #print("COMBINE MODE FOR OBJECT", combine_mode)
            if combine_mode == 'Embed':
                level_needs_export = True
                break
            elif combine_mode == 'EmbedExternal' and not blueprint.local:
                level_needs_export = True
                break
        # changes => list of changed objects (regardless of wether they have been changed in main scene or in lib scene)
        # wich of those objects are blueprint instances
        # we need a list of changed objects that are blueprint instances
        return level_needs_export
    return False


# this also takes the split/embed mode into account: if a collection instance changes AND embed is active, its container level/world should also be exported
def get_levels_to_export(changes_per_scene, changed_export_parameters, blueprints_data, addon_prefs):
    export_gltf_extension = getattr(addon_prefs, "export_gltf_extension")
    export_levels_path_full = getattr(addon_prefs, "export_levels_path_full")

    change_detection = getattr(addon_prefs.auto_export, "change_detection")
    collection_instances_combine_mode = getattr(addon_prefs.auto_export, "collection_instances_combine_mode")

    [main_scene_names, level_scenes, library_scene_names, library_scenes] = get_scenes(addon_prefs)
 
    # determine list of main scenes to export
    # we have more relaxed rules to determine if the main scenes have changed : any change is ok, (allows easier handling of changes, render settings etc)
    main_scenes_to_export = [scene_name for scene_name in main_scene_names if not change_detection or changed_export_parameters or scene_name in changes_per_scene.keys() or changed_object_in_scene(scene_name, changes_per_scene, blueprints_data, collection_instances_combine_mode) or not check_if_blueprint_on_disk(scene_name, export_levels_path_full, export_gltf_extension) ]

    return (main_scenes_to_export)