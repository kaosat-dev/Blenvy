import os
import bpy

from ..generate_and_export import generate_and_export
from .export_gltf import (generate_gltf_export_preferences, export_gltf)
from ..bevy_dynamic import is_object_dynamic, is_object_static
from ..helpers_scenes import clear_hollow_scene, copy_hollowed_collection_into


# export all main scenes
def export_main_scenes(scenes, folder_path, addon_prefs): 
    for scene in scenes:
        export_main_scene(scene, folder_path, addon_prefs)

def export_main_scene(scene, folder_path, addon_prefs, library_collections): 
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    export_output_folder = getattr(addon_prefs,"export_output_folder")
    export_blueprints = getattr(addon_prefs,"export_blueprints")
    export_separate_dynamic_and_static_objects = getattr(addon_prefs, "export_separate_dynamic_and_static_objects")
    collection_instances_combine_mode = getattr(addon_prefs, "collection_instances_combine_mode")

    gltf_output_path = os.path.join(folder_path, export_output_folder, scene.name)
    export_settings = { **gltf_export_preferences, 
                       'use_active_scene': True, 
                       'use_active_collection':True, 
                       'use_active_collection_with_nested':True,  
                       'use_visible': False,
                       'use_renderable': False,
                       'export_apply':True
                       }

    if export_blueprints : 
        if export_separate_dynamic_and_static_objects:
            #print("SPLIT STATIC AND DYNAMIC")
            # first export static objects
            generate_and_export(
                addon_prefs, 
                temp_scene_name="__temp_scene",
                export_settings=export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(scene.collection, temp_collection, library_collections=library_collections, collection_instances_combine_mode= collection_instances_combine_mode, filter=is_object_static),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=scene.collection, temp_scene=temp_scene, **params)
            )

            # then export all dynamic objects
            gltf_output_path = os.path.join(folder_path, export_output_folder, scene.name+ "_dynamic")
            generate_and_export(
                addon_prefs, 
                temp_scene_name="__temp_scene",
                export_settings=export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(scene.collection, temp_collection, library_collections=library_collections, collection_instances_combine_mode= collection_instances_combine_mode, filter=is_object_dynamic),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=scene.collection, temp_scene=temp_scene, **params)
            )

        else:
            #print("NO SPLIT")
            generate_and_export(
                addon_prefs, 
                temp_scene_name="__temp_scene",
                export_settings=export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(scene.collection, temp_collection, library_collections=library_collections, collection_instances_combine_mode= collection_instances_combine_mode),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=scene.collection, temp_scene=temp_scene, **params)
            )

    else:
        print("       exporting gltf to", gltf_output_path, ".gltf/glb")
        export_gltf(gltf_output_path, export_settings)



