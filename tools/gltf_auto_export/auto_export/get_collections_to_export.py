import os
import bpy

from .get_standard_exporter_settings import get_standard_exporter_settings
from .export_blueprints import check_if_blueprint_on_disk, check_if_blueprints_exist, export_blueprints_from_collections
from ..helpers.helpers_collections import get_exportable_collections
from ..helpers.helpers_collections import (get_collections_in_library, get_exportable_collections, get_collections_per_scene, find_collection_ascendant_target_collection)
from ..helpers.helpers_scenes import (get_scenes, )

def get_collections_to_export(folder_path, export_output_folder, changes_per_scene, changed_export_parameters, addon_prefs):
    export_change_detection = getattr(addon_prefs, "export_change_detection")
    export_materials_library = getattr(addon_prefs,"export_materials_library")

    # standard gltf export settings are stored differently
    standard_gltf_exporter_settings = get_standard_exporter_settings()
    [main_scene_names, level_scenes, library_scene_names, library_scenes] = get_scenes(addon_prefs)

    collection_parents = dict()
    for collection in bpy.data.collections:
        collection_parents[collection.name] = None
    for collection in bpy.data.collections:
        for ch in collection.children:
            collection_parents[ch.name] = collection.name

    # get a list of all collections actually in use
    (collections, blueprint_hierarchy) = get_exportable_collections(level_scenes, library_scenes, addon_prefs)

    # first check if all collections have already been exported before (if this is the first time the exporter is run
    # in your current Blender session for example)
    export_blueprints_path = os.path.join(folder_path, export_output_folder, getattr(addon_prefs,"export_blueprints_path")) if getattr(addon_prefs,"export_blueprints_path") != '' else folder_path
    export_levels_path = os.path.join(folder_path, export_output_folder)

    gltf_extension = standard_gltf_exporter_settings.get("export_format", 'GLB')
    gltf_extension = '.glb' if gltf_extension == 'GLB' else '.gltf'
    collections_not_on_disk = check_if_blueprints_exist(collections, export_blueprints_path, gltf_extension)
    changed_collections = []

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

    collections_to_export =  list(set(changed_collections + collections_not_on_disk)) if export_change_detection else collections

    # we need to re_export everything if the export parameters have been changed # TODO: perhaps do this BEFORE the rest above for better perfs
    collections_to_export = collections if changed_export_parameters else collections_to_export
    collections_per_scene = get_collections_per_scene(collections_to_export, library_scenes)
    
    # collections that do not come from a library should not be exported as seperate blueprints
    # FIMXE: logic is erroneous, needs to be changed
    library_collections = get_collections_in_library(library_scenes)
    collections_to_export = list(set(collections_to_export).intersection(set(library_collections)))


    main_scenes_to_export = [scene_name for scene_name in main_scene_names if not export_change_detection or changed_export_parameters or scene_name in changes_per_scene.keys() or not check_if_blueprint_on_disk(scene_name, export_levels_path, gltf_extension)]

    # update the list of tracked exports
    exports_total = len(collections_to_export) + len(main_scenes_to_export) + (1 if export_materials_library else 0)
    bpy.context.window_manager.auto_export_tracker.exports_total = exports_total
    bpy.context.window_manager.auto_export_tracker.exports_count = exports_total



    print("-------------------------------")
    print("collections:               all:", collections)
    print("collections:           changed:", changed_collections)
    print("collections: not found on disk:", collections_not_on_disk)
    print("collections:        in library:", library_collections)
    print("collections:         to export:", collections_to_export)
    print("collections:         per_scene:", collections_per_scene)
    print("-------------------------------")
    print("BLUEPRINTS:          to export:", collections_to_export)
    print("-------------------------------")
    print("MAIN SCENES:         to export:", main_scenes_to_export)
    print("-------------------------------")

    return (collections, collections_to_export, main_scenes_to_export, library_collections, collections_per_scene, blueprint_hierarchy, export_levels_path, gltf_extension)