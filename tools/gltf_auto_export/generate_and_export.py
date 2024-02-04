import bpy
from .auto_export.export_gltf import export_gltf
from .helpers_collections import (set_active_collection)

""" 
generates a temporary scene, fills it with data, cleans up after itself
    * named using temp_scene_name 
    * filled using the tempScene_filler
    * written on disk to gltf_output_path, with the gltf export parameters in export_settings
    * cleaned up using tempScene_cleaner

"""
def generate_and_export(addon_prefs, export_settings, gltf_output_path, temp_scene_name="__temp_scene", tempScene_filler=None, tempScene_cleaner=None): 

    temp_scene = bpy.data.scenes.new(name=temp_scene_name)
    temp_root_collection = temp_scene.collection

    # save active scene
    original_scene = bpy.context.window.scene
    # and selected collection
    original_collection = bpy.context.view_layer.active_layer_collection
    # we set our active scene to be this one : this is needed otherwise the stand-in empties get generated in the wrong scene
    bpy.context.window.scene = temp_scene

    with bpy.context.temp_override(scene=temp_scene):
        # print("context inside", bpy.context.scene)
        # detect scene mistmatch
        # print("bpy.context.scene.name != bpy.context.window.scene.name", bpy.context.scene.name, bpy.context.window.scene.name)
        scene_mismatch = bpy.context.scene.name != bpy.context.window.scene.name
        if scene_mismatch:
            raise Exception("Context scene mismatch, aborting", bpy.context.scene.name, bpy.context.window.scene.name)
        
        set_active_collection(bpy.context.scene, temp_root_collection.name)
        # generate contents of temporary scene
        scene_filler_data = tempScene_filler(temp_root_collection)
        # export the temporary scene
        export_gltf(gltf_output_path, export_settings)
        # restore everything
        tempScene_cleaner(temp_scene, scene_filler_data)

    # reset active scene
    bpy.context.window.scene = original_scene
    # reset active collection
    bpy.context.view_layer.active_layer_collection = original_collection
