import os
import bpy

from ..constants import TEMPSCENE_PREFIX
from ..helpers.generate_and_export import generate_and_export
from .export_gltf import (generate_gltf_export_preferences)
from ..helpers.helpers_scenes import clear_hollow_scene, copy_hollowed_collection_into

   
def export_blueprints(blueprints, addon_prefs, blueprints_data):
    export_blueprints_path_full = getattr(addon_prefs, "export_blueprints_path_full")
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    
    try:
        # save current active collection
        active_collection =  bpy.context.view_layer.active_layer_collection
        export_materials_library = getattr(addon_prefs.auto_export, "export_materials_library")

        for blueprint in blueprints:
            print("exporting collection", blueprint.name)
            gltf_output_path = os.path.join(export_blueprints_path_full, blueprint.name)
            export_settings = { **gltf_export_preferences, 'use_active_scene': True, 'use_active_collection': True, 'use_active_collection_with_nested':True}
            
            # if we are using the material library option, do not export materials, use placeholder instead
            if export_materials_library:
                export_settings['export_materials'] = 'PLACEHOLDER'

            collection = bpy.data.collections[blueprint.name]
            # do the actual export
            generate_and_export(
                addon_prefs, 
                temp_scene_name=TEMPSCENE_PREFIX+collection.name,
                export_settings=export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(collection, temp_collection, blueprints_data=blueprints_data, addon_prefs=addon_prefs),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=collection, temp_scene=temp_scene, **params)
            )

        # reset active collection to the one we save before
        bpy.context.view_layer.active_layer_collection = active_collection

    except Exception as error:
        print("failed to export collections to gltf: ", error)
        raise error

