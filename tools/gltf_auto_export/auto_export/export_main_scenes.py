import os
import bpy

from ..constants import TEMPSCENE_PREFIX
from ..helpers.generate_and_export import generate_and_export
from .export_gltf import (generate_gltf_export_preferences, export_gltf)
from ..modules.bevy_dynamic import is_object_dynamic, is_object_static
from ..helpers.helpers_scenes import clear_hollow_scene, copy_hollowed_collection_into
from ..helpers.helpers_blueprints import inject_blueprints_list_into_main_scene, remove_blueprints_list_from_main_scene

# export all main scenes
def export_main_scenes(scenes, folder_path, addon_prefs): 
    for scene in scenes:
        export_main_scene(scene, folder_path, addon_prefs)

def export_main_scene(scene, folder_path, addon_prefs, blueprints_data): 
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    export_output_folder = getattr(addon_prefs,"export_output_folder")
    export_blueprints = getattr(addon_prefs,"export_blueprints")
    export_separate_dynamic_and_static_objects = getattr(addon_prefs, "export_separate_dynamic_and_static_objects")

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
        
        inject_blueprints_list_into_main_scene(scene, blueprints_data)

        if export_separate_dynamic_and_static_objects:
            #print("SPLIT STATIC AND DYNAMIC")
            # first export static objects
            generate_and_export(
                addon_prefs, 
                temp_scene_name=TEMPSCENE_PREFIX,
                export_settings=export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(scene.collection, temp_collection, blueprints_data=blueprints_data, filter=is_object_static, addon_prefs=addon_prefs),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=scene.collection, temp_scene=temp_scene, **params)
            )

            # then export all dynamic objects
            gltf_output_path = os.path.join(folder_path, export_output_folder, scene.name+ "_dynamic")
            generate_and_export(
                addon_prefs, 
                temp_scene_name=TEMPSCENE_PREFIX,
                export_settings=export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(scene.collection, temp_collection, blueprints_data=blueprints_data, filter=is_object_dynamic, addon_prefs=addon_prefs),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=scene.collection, temp_scene=temp_scene, **params)
            )

        else:
            #print("NO SPLIT")
            generate_and_export(
                addon_prefs, 
                temp_scene_name=TEMPSCENE_PREFIX,
                export_settings=export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(scene.collection, temp_collection, blueprints_data=blueprints_data, addon_prefs=addon_prefs),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=scene.collection, temp_scene=temp_scene, **params)
            )

    else:
        print("       exporting gltf to", gltf_output_path, ".gltf/glb")
        export_gltf(gltf_output_path, export_settings)

    remove_blueprints_list_from_main_scene(scene)



