import os
import bpy

from .export_blueprints import check_if_blueprint_on_disk, check_if_blueprints_exist, export_blueprints_from_collections
from ..helpers.helpers_collections import get_exportable_collections
from ..helpers.helpers_collections import (get_collections_in_library, get_exportable_collections, get_collections_per_scene, find_collection_ascendant_target_collection)
from ..helpers.helpers_scenes import (get_scenes, )

def get_collections_to_export(changes_per_scene, changed_export_parameters, addon_prefs):
    export_change_detection = getattr(addon_prefs, "export_change_detection")
    export_gltf_extension = getattr(addon_prefs, "export_gltf_extension", ".glb")
    export_blueprints_path = getattr(addon_prefs,"export_blueprints_path", "")

    [main_scene_names, level_scenes, library_scene_names, library_scenes] = get_scenes(addon_prefs)
    # get a list of all collections actually in use
    (collections, blueprint_hierarchy) = get_exportable_collections(level_scenes, library_scenes, addon_prefs)
    collections_to_export = collections # just for clarity

    print("export_change_detection", export_change_detection, export_gltf_extension, export_blueprints_path)
    
    # if the export parameters have changed, bail out early
    # we need to re_export everything if the export parameters have been changed
    if export_change_detection and not changed_export_parameters:
        changed_collections = []

        # first check if all collections have already been exported before (if this is the first time the exporter is run
        # in your current Blender session for example)
        collections_not_on_disk = check_if_blueprints_exist(collections, export_blueprints_path, export_gltf_extension)

        # create parent relations for all collections # TODO: optimise this
        collection_parents = dict()
        for collection in bpy.data.collections:
            collection_parents[collection.name] = None
        for collection in bpy.data.collections:
            for ch in collection.children:
                collection_parents[ch.name] = collection.name

        # determine which collections have changed
        for scene, objects in changes_per_scene.items():
            print("  changed scene", scene)
            for obj_name, obj in objects.items():
                object_collections = list(obj.users_collection) if hasattr(obj, 'users_collection') else []
                object_collection_names = list(map(lambda collection: collection.name, object_collections))

                if len(object_collection_names) > 1:
                    print("ERRROR for",obj_name,"objects in multiple collections not supported")
                else:
                    object_collection_name =  object_collection_names[0] if len(object_collection_names) > 0 else None
                    #recurse updwards until we find one of our collections (or not)
                    matching_collection = find_collection_ascendant_target_collection(collection_parents, collections, object_collection_name)
                    if matching_collection is not None:
                        changed_collections.append(matching_collection)

        collections_to_export =  list(set(changed_collections + collections_not_on_disk))

    # this needs to be done based on all previously collected collections, not the ones that we filter out based on their presence in the library scenes
    collections_per_scene = get_collections_per_scene(collections_to_export, library_scenes)
    
    # collections that do not come from a library should not be exported as seperate blueprints
    # FIMXE: logic is erroneous, needs to be changed
    library_collections = get_collections_in_library(library_scenes)
    collections_to_export = list(set(collections_to_export).intersection(set(library_collections)))

    # all collections, collections to export     
    return (collections, collections_to_export, library_collections, collections_per_scene)