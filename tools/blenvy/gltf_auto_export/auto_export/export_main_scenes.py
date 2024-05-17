import os
import bpy
from pathlib import Path

from ..constants import TEMPSCENE_PREFIX
from ..helpers.generate_and_export import generate_and_export
from .export_gltf import (generate_gltf_export_preferences, export_gltf)
from ..modules.bevy_dynamic import is_object_dynamic, is_object_static
from ..helpers.helpers_scenes import clear_hollow_scene, copy_hollowed_collection_into
from ...blueprints.blueprint_helpers import inject_blueprints_list_into_main_scene, remove_blueprints_list_from_main_scene

def export_main_scene(scene, blend_file_path, addon_prefs, blueprints_data): 
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    export_assets_path_full = getattr(addon_prefs,"export_assets_path_full")
    export_levels_path_full = getattr(addon_prefs,"export_levels_path_full")

    export_blueprints = getattr(addon_prefs.auto_export,"export_blueprints")
    export_separate_dynamic_and_static_objects = getattr(addon_prefs.auto_export, "export_separate_dynamic_and_static_objects")

    export_settings = { **gltf_export_preferences, 
                       'use_active_scene': True, 
                       'use_active_collection':True, 
                       'use_active_collection_with_nested':True,  
                       'use_visible': False,
                       'use_renderable': False,
                       'export_apply':True
                       }

    if export_blueprints : 
        gltf_output_path = os.path.join(export_levels_path_full, scene.name)

        #inject_blueprints_list_into_main_scene(scene, blueprints_data, addon_prefs)
        return
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
            gltf_output_path = os.path.join(export_levels_path_full, scene.name+ "_dynamic")
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
        gltf_output_path = os.path.join(export_assets_path_full, scene.name)
        print("       exporting gltf to", gltf_output_path, ".gltf/glb")
        export_gltf(gltf_output_path, export_settings)

    remove_blueprints_list_from_main_scene(scene)



