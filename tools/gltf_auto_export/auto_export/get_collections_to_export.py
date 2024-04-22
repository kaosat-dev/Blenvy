import bpy

from ..helpers.helpers_scenes import (get_scenes, )
from ..helpers.helpers_blueprints import find_blueprints_not_on_disk

# TODO: this should also take the split/embed mode into account: if a nested collection changes AND embed is active, its container collection should also be exported
def get_collections_to_export(changes_per_scene, changed_export_parameters, blueprints_data, addon_prefs):
    export_change_detection = getattr(addon_prefs, "export_change_detection")
    export_gltf_extension = getattr(addon_prefs, "export_gltf_extension", ".glb")
    export_blueprints_path = getattr(addon_prefs,"export_blueprints_path", "")
    collection_instances_combine_mode = getattr(addon_prefs, "collection_instances_combine_mode")

    [main_scene_names, level_scenes, library_scene_names, library_scenes] = get_scenes(addon_prefs)
    internal_blueprints = blueprints_data.internal_blueprints
    blueprints_to_export = internal_blueprints # just for clarity

    # print("export_change_detection", export_change_detection, "changed_export_parameters", changed_export_parameters, "changes_per_scene", changes_per_scene)
    
    # if the export parameters have changed, bail out early
    # we need to re_export everything if the export parameters have been changed
    if export_change_detection and not changed_export_parameters:
        changed_blueprints = []

        # first check if all collections have already been exported before (if this is the first time the exporter is run
        # in your current Blender session for example)
        blueprints_not_on_disk = find_blueprints_not_on_disk(internal_blueprints, export_blueprints_path, export_gltf_extension)

        for scene in library_scenes:
            if scene.name in changes_per_scene:
                print("scanning", scene.name)
                changed_objects = list(changes_per_scene[scene.name].keys())
                changed_blueprints = [blueprints_data.blueprints_from_objects[changed] for changed in changed_objects if changed in blueprints_data.blueprints_from_objects]
                print("changed_blueprints", changed_blueprints)
                # we only care about local blueprints/collections
                changed_local_blueprints = [blueprint for blueprint in changed_blueprints if blueprint.name in blueprints_data.blueprints_per_name.keys() and blueprint.local]
                print("changed_local_blueprints blueprints", changed_local_blueprints)
                changed_blueprints += changed_local_blueprints

        print("CHANGED BLUEPRINTS", changed_blueprints)
    
        blueprints_to_export =  list(set(changed_blueprints + blueprints_not_on_disk))
    
    # changed/all blueprints to export     
    return (blueprints_to_export)