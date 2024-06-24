import os
import bpy
from blenvy.assets.assets_scan import get_blueprint_asset_tree
from blenvy.assets.generate_asset_file import write_ron_assets_file
from ..constants import TEMPSCENE_PREFIX
from ..common.generate_temporary_scene_and_export import generate_temporary_scene_and_export, copy_hollowed_collection_into, clear_hollow_scene
from ..common.export_gltf import generate_gltf_export_settings

def assets_to_fake_ron(list_like):
    result = []
    for item in list_like:
        result.append(f"(name: \"{item['name']}\", path: \"{item['path']}\")")
    return f"({result})".replace("'", '')#.join(", ")

def export_blueprints(blueprints, settings, blueprints_data):
    blueprints_path_full = getattr(settings, "blueprints_path_full")
    gltf_export_settings = generate_gltf_export_settings(settings)
    
    try:
        # save current active collection
        active_collection =  bpy.context.view_layer.active_layer_collection
        export_materials_library = getattr(settings.auto_export, "export_materials_library")

        for blueprint in blueprints:
            print("exporting collection", blueprint.name)
            gltf_output_path = os.path.join(blueprints_path_full, blueprint.name) # TODO: reuse the export_path custom property ?
            gltf_export_settings = { **gltf_export_settings, 'use_active_scene': True, 'use_active_collection': True, 'use_active_collection_with_nested':True}
            
            # if we are using the material library option, do not export materials, use placeholder instead
            if export_materials_library:
                gltf_export_settings['export_materials'] = 'PLACEHOLDER'

            collection = bpy.data.collections[blueprint.name]

            print("BLUEPRINT", blueprint.name)

            for asset in collection.user_assets:
                print("  user asset", asset.name, asset.path)

            all_assets = []
            auto_assets = []
            collection["BlenvyAssets"] = assets_to_fake_ron([]) #assets_to_fake_ron([{"name": asset.name, "path": asset.path} for asset in collection.user_assets] + auto_assets) #all_assets + [{"name": asset.name, "path": asset.path} for asset in collection.user_assets] + auto_assets)


            # do the actual export
            generate_temporary_scene_and_export(
                settings, 
                temp_scene_name=TEMPSCENE_PREFIX+collection.name,
                additional_data = collection,
                gltf_export_settings=gltf_export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(collection, temp_collection, blueprints_data=blueprints_data, settings=settings),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=collection, temp_scene=temp_scene, **params)
            )

            #blueprint_asset_tree = get_blueprint_asset_tree(blueprint=blueprint, blueprints_data=blueprints_data, settings=settings)
            #write_ron_assets_file(blueprint.name, blueprint_asset_tree, output_path_full = blueprints_path_full)

        # reset active collection to the one we save before
        bpy.context.view_layer.active_layer_collection = active_collection

    except Exception as error:
        print("failed to export collections to gltf: ", error)
        raise error

