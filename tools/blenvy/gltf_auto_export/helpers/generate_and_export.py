import bpy
from ..auto_export.export_gltf import export_gltf
from ...core.helpers_collections import (set_active_collection)

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
    # and mode
    original_mode = bpy.context.active_object.mode if bpy.context.active_object != None else None
    # we change the mode to object mode, otherwise the gltf exporter is not happy
    if original_mode != None and original_mode != 'OBJECT':
        print("setting to object mode", original_mode)
        bpy.ops.object.mode_set(mode='OBJECT')
    # we set our active scene to be this one : this is needed otherwise the stand-in empties get generated in the wrong scene
    bpy.context.window.scene = temp_scene

    area = [area for area in bpy.context.screen.areas if area.type == "VIEW_3D"][0]
    region = [region for region in area.regions if region.type == 'WINDOW'][0]
    with bpy.context.temp_override(scene=temp_scene, area=area, region=region):
        # detect scene mistmatch
        scene_mismatch = bpy.context.scene.name != bpy.context.window.scene.name
        if scene_mismatch:
            raise Exception("Context scene mismatch, aborting", bpy.context.scene.name, bpy.context.window.scene.name)
        
        set_active_collection(bpy.context.scene, temp_root_collection.name)
        # generate contents of temporary scene
        scene_filler_data = tempScene_filler(temp_root_collection)
        # export the temporary scene
        try:
            export_gltf(gltf_output_path, export_settings)
        except Exception as error:
            print("failed to export gltf !", error)
            raise error
        # restore everything
        tempScene_cleaner(temp_scene, scene_filler_data)

    # reset active scene
    bpy.context.window.scene = original_scene
    # reset active collection
    bpy.context.view_layer.active_layer_collection = original_collection
    # reset mode
    if original_mode != None:
        bpy.ops.object.mode_set( mode = original_mode )

