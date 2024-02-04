import os
import bpy


from .object_makers import make_empty
from .export_gltf import (export_gltf, generate_gltf_export_preferences)
from ..helpers_collections import find_layer_collection_recursive, recurLayerCollection
from ..helpers_scenes import clear_hollow_scene, generate_hollow_scene

# export collections: all the collections that have an instance in the main scene AND any marked collections, even if they do not have instances
def export_collections(collections, folder_path, library_scene, addon_prefs, gltf_export_preferences, blueprint_hierarchy, library_collections): 
    # set active scene to be the library scene (hack for now)
    bpy.context.window.scene = library_scene
    # save current active collection
    active_collection =  bpy.context.view_layer.active_layer_collection
    export_materials_library = getattr(addon_prefs,"export_materials_library")

    for collection_name in collections:
        print("exporting collection", collection_name)
        layer_collection = bpy.data.scenes[library_scene.name].view_layers['ViewLayer'].layer_collection
        layerColl = recurLayerCollection(layer_collection, collection_name)
        # set active collection to the collection
        bpy.context.view_layer.active_layer_collection = layerColl
        gltf_output_path = os.path.join(folder_path, collection_name)

        export_settings = { **gltf_export_preferences, 'use_active_scene': True, 'use_active_collection': True, 'use_active_collection_with_nested':True}
        
        # if we are using the material library option, do not export materials, use placeholder instead
        if export_materials_library:
            export_settings['export_materials'] = 'PLACEHOLDER'

        #if relevant we replace sub collections instances with placeholders too
        # this is not needed if a collection/blueprint does not have sub blueprints or sub collections
        collection_in_blueprint_hierarchy = collection_name in blueprint_hierarchy and len(blueprint_hierarchy[collection_name]) > 0
        collection_has_child_collections = len(bpy.data.collections[collection_name].children) > 0
        if collection_in_blueprint_hierarchy or collection_has_child_collections:
            #print("generate hollow scene for nested blueprints", library_collections)
            backup = bpy.context.window.scene
            collection = bpy.data.collections[collection_name]
            (hollow_scene, temporary_collections, root_objects, special_properties) = generate_hollow_scene(collection, library_collections, addon_prefs, name="__temp_scene_"+collection.name)

            export_gltf(gltf_output_path, export_settings)

            clear_hollow_scene(hollow_scene, collection, temporary_collections, root_objects, special_properties)
            bpy.context.window.scene = backup
        else:
            #print("standard export")
            export_gltf(gltf_output_path, export_settings)

    # reset active collection to the one we save before
    bpy.context.view_layer.active_layer_collection = active_collection


def export_blueprints_from_collections(collections, library_scene, folder_path, addon_prefs, blueprint_hierarchy, library_collections):
    export_output_folder = getattr(addon_prefs,"export_output_folder")
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    export_blueprints_path = os.path.join(folder_path, export_output_folder, getattr(addon_prefs,"export_blueprints_path")) if getattr(addon_prefs,"export_blueprints_path") != '' else folder_path

    #print("-----EXPORTING BLUEPRINTS----")
    #print("LIBRARY EXPORT", export_blueprints_path )

    try:
        export_collections(collections, export_blueprints_path, library_scene, addon_prefs, gltf_export_preferences, blueprint_hierarchy, library_collections)
    except Exception as error:
        print("failed to export collections to gltf: ", error)
        # TODO : rethrow
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

