import bpy
import os
from ..helpers.helpers_scenes import (get_scenes, )
from ...blueprints.blueprint_helpers import find_blueprints_not_on_disk

# TODO: this should also take the split/embed mode into account: if a nested collection changes AND embed is active, its container collection should also be exported
def get_blueprints_to_export(changes_per_scene, changed_export_parameters, blueprints_data, addon_prefs):
    export_gltf_extension = getattr(addon_prefs, "export_gltf_extension", ".glb")
    export_blueprints_path_full = getattr(addon_prefs,"export_blueprints_path_full", "")
    change_detection = getattr(addon_prefs.auto_export, "change_detection")
    collection_instances_combine_mode = getattr(addon_prefs.auto_export, "collection_instances_combine_mode")

    [main_scene_names, level_scenes, library_scene_names, library_scenes] = get_scenes(addon_prefs)
    internal_blueprints = blueprints_data.internal_blueprints
    blueprints_to_export = internal_blueprints # just for clarity

    # print("change_detection", change_detection, "changed_export_parameters", changed_export_parameters, "changes_per_scene", changes_per_scene)
    
    # if the export parameters have changed, bail out early
    # we need to re_export everything if the export parameters have been changed
    if change_detection and not changed_export_parameters:
        changed_blueprints = []

        # first check if all collections have already been exported before (if this is the first time the exporter is run
        # in your current Blender session for example)
        blueprints_not_on_disk = find_blueprints_not_on_disk(internal_blueprints, export_blueprints_path_full, export_gltf_extension)

        for scene in library_scenes:
            if scene.name in changes_per_scene:
                changed_objects = list(changes_per_scene[scene.name].keys())
                changed_blueprints = [blueprints_data.blueprints_from_objects[changed] for changed in changed_objects if changed in blueprints_data.blueprints_from_objects]
                # we only care about local blueprints/collections
                changed_local_blueprints = [blueprint for blueprint in changed_blueprints if blueprint.name in blueprints_data.blueprints_per_name.keys() and blueprint.local]
                # FIXME: double check this: why are we combining these two ?
                changed_blueprints += changed_local_blueprints

       
        blueprints_to_export =  list(set(changed_blueprints + blueprints_not_on_disk))


    # filter out blueprints that are not marked & deal with the different combine modes
    # we check for blueprint & object specific overrides ...
    filtered_blueprints = []
    for blueprint in blueprints_to_export:
        if blueprint.marked:
            filtered_blueprints.append(blueprint)
        else:
            blueprint_instances = blueprints_data.internal_collection_instances.get(blueprint.name, [])
            # print("INSTANCES", blueprint_instances, blueprints_data.internal_collection_instances)
            # marked blueprints that have changed are always exported, regardless of whether they are in use (have instances) or not 
            for blueprint_instance in blueprint_instances:
                combine_mode = blueprint_instance['_combine'] if '_combine' in blueprint_instance else collection_instances_combine_mode
                if combine_mode == "Split": # we only keep changed blueprints if mode is set to split for at least one instance (aka if ALL instances of a blueprint are merged, do not export ? )  
                    filtered_blueprints.append(blueprint)

        blueprints_to_export =  list(set(filtered_blueprints))

    
    # changed/all blueprints to export     
    return (blueprints_to_export)