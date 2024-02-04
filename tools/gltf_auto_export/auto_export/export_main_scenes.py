import os
import bpy
from .export_gltf import (generate_gltf_export_preferences, export_gltf)
from ..bevy_dynamic import is_object_dynamic, is_object_static
from ..helpers_scenes import clear_hollow_scene, generate_hollow_scene


# export all main scenes
def export_main_scenes(scenes, folder_path, addon_prefs): 
    for scene in scenes:
        export_main_scene(scene, folder_path, addon_prefs)

def export_main_scene(scene, folder_path, addon_prefs, library_collections): 
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
        if export_separate_dynamic_and_static_objects:
            #print("SPLIT STATIC AND DYNAMIC")
            # first export all dynamic objects
            (hollow_scene, temporary_collections, root_objects, special_properties) = generate_hollow_scene(scene, library_collections, addon_prefs, is_object_dynamic) 
            gltf_output_path = os.path.join(folder_path, export_output_folder, scene.name+ "_dynamic")
            # set active scene to be the given scene
            bpy.context.window.scene = hollow_scene
            print("       exporting gltf to", gltf_output_path, ".gltf/glb")
            export_gltf(gltf_output_path, export_settings)
            clear_hollow_scene(hollow_scene, scene.collection, temporary_collections, root_objects, special_properties)


            # now export static objects
            (hollow_scene, temporary_collections, root_objects, special_properties) = generate_hollow_scene(scene, library_collections, addon_prefs, is_object_static) 
            gltf_output_path = os.path.join(folder_path, export_output_folder, scene.name)
            # set active scene to be the given scene
            bpy.context.window.scene = hollow_scene
            print("       exporting gltf to", gltf_output_path, ".gltf/glb")
            export_gltf(gltf_output_path, export_settings)
            clear_hollow_scene(hollow_scene, scene.collection, temporary_collections, root_objects, special_properties)

        else:
            #print("NO SPLIT")

            # todo: add exception handling
            (hollow_scene, temporary_collections, root_objects, special_properties) = generate_hollow_scene(scene.collection, library_collections, addon_prefs, name="__temp_scene") 
            # set active scene to be the given scene
            bpy.context.window.scene = hollow_scene
            print("context scene", bpy.context.scene, "window scene", bpy.context.window.scene, bpy.context.scene == bpy.context.window.scene)

            with bpy.context.temp_override(scene=hollow_scene):
                print("context inside", bpy.context.scene)

            print("       exporting gltf to", gltf_output_path, ".gltf/glb")
            export_gltf(gltf_output_path, export_settings)

            clear_hollow_scene(hollow_scene, scene.collection, temporary_collections, root_objects, special_properties)
    else:
        print("       exporting gltf to", gltf_output_path, ".gltf/glb")
        export_gltf(gltf_output_path, export_settings)



