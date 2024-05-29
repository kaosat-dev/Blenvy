import os
import bpy
from ..constants import TEMPSCENE_PREFIX
from ..common.generate_temporary_scene_and_export import generate_temporary_scene_and_export, copy_hollowed_collection_into, clear_hollow_scene
from ..common.export_gltf import generate_gltf_export_settings

def export_blueprints(blueprints, settings, blueprints_data):
    blueprints_path_full = getattr(settings, "blueprints_path_full")
    gltf_export_settings = generate_gltf_export_settings(settings)
    
    try:
        # save current active collection
        active_collection =  bpy.context.view_layer.active_layer_collection
        export_materials_library = getattr(settings.auto_export, "export_materials_library")

        for blueprint in blueprints:
            print("exporting collection", blueprint.name)
            gltf_output_path = os.path.join(blueprints_path_full, blueprint.name)
            gltf_export_settings = { **gltf_export_settings, 'use_active_scene': True, 'use_active_collection': True, 'use_active_collection_with_nested':True}
            
            # if we are using the material library option, do not export materials, use placeholder instead
            if export_materials_library:
                gltf_export_settings['export_materials'] = 'PLACEHOLDER'

            collection = bpy.data.collections[blueprint.name]
            # do the actual export
            generate_temporary_scene_and_export(
                settings, 
                temp_scene_name=TEMPSCENE_PREFIX+collection.name,
                gltf_export_settings=gltf_export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(collection, temp_collection, blueprints_data=blueprints_data, settings=settings),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=collection, temp_scene=temp_scene, **params)
            )

        # reset active collection to the one we save before
        bpy.context.view_layer.active_layer_collection = active_collection

    except Exception as error:
        print("failed to export collections to gltf: ", error)
        raise error

