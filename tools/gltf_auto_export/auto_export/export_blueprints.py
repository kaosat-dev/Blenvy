import os
import bpy

from ..helpers.generate_and_export import generate_and_export
from .export_gltf import (generate_gltf_export_preferences)
from ..helpers.helpers_scenes import clear_hollow_scene, copy_hollowed_collection_into

# export collections: all the collections that have an instance in the main scene AND any marked collections, even if they do not have instances
def export_collections(collections, folder_path, library_scene, addon_prefs, gltf_export_preferences, blueprint_hierarchy, library_collections): 
   
    # save current active collection
    active_collection =  bpy.context.view_layer.active_layer_collection
    export_materials_library = getattr(addon_prefs,"export_materials_library")

    for collection_name in collections:
        print("exporting collection", collection_name)
        gltf_output_path = os.path.join(folder_path, collection_name)
        export_settings = { **gltf_export_preferences, 'use_active_scene': True, 'use_active_collection': True, 'use_active_collection_with_nested':True}
        
        # if we are using the material library option, do not export materials, use placeholder instead
        if export_materials_library:
            export_settings['export_materials'] = 'PLACEHOLDER'

        collection = bpy.data.collections[collection_name]
        collection_instances_combine_mode = getattr(addon_prefs, "collection_instances_combine_mode")
        generate_and_export(
            addon_prefs, 
            temp_scene_name="__temp_scene_"+collection.name,
            export_settings=export_settings,
            gltf_output_path=gltf_output_path,
            tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(collection, temp_collection, library_collections=library_collections, collection_instances_combine_mode= collection_instances_combine_mode),
            tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=collection, temp_scene=temp_scene, **params)
        )
    # reset active collection to the one we save before
    bpy.context.view_layer.active_layer_collection = active_collection


def export_blueprints_from_collections(collections, library_scene, folder_path, addon_prefs, blueprint_hierarchy, library_collections):
    export_output_folder = getattr(addon_prefs,"export_output_folder")
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    export_blueprints_path = os.path.join(folder_path, export_output_folder, getattr(addon_prefs,"export_blueprints_path")) if getattr(addon_prefs,"export_blueprints_path") != '' else folder_path

    try:
        export_collections(collections, export_blueprints_path, library_scene, addon_prefs, gltf_export_preferences, blueprint_hierarchy, library_collections)
    except Exception as error:
        print("failed to export collections to gltf: ", error)
        raise error

# TODO : add a flag to also search of deeply nested components
def get_nested_components(object):
    if object.instance_type == 'COLLECTION':
        collection_name = object.instance_collection.name
        collection = bpy.data.collections[collection_name]
        all_objects = collection.all_objects
        result = []
        for object in all_objects:
            components = dict(object)
            if len(components.keys()) > 0:
                result += [(object, components)]
        return result
    return []
        #for collection in traverse_tree(collection):
        #    for object in collection.all_objects


def check_if_blueprints_exist(collections, folder_path, extension):
    not_found_blueprints = []
    for collection_name in collections:
        gltf_output_path = os.path.join(folder_path, collection_name + extension)
        # print("gltf_output_path", gltf_output_path)
        found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
        if not found:
            not_found_blueprints.append(collection_name)
    return not_found_blueprints


def check_if_blueprint_on_disk(scene_name, folder_path, extension):
    gltf_output_path = os.path.join(folder_path, scene_name + extension)
    found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
    print("level", scene_name, "found", found, "path", gltf_output_path)
    return found

