import json
import os
from pathlib import Path
from types import SimpleNamespace

import bpy
from blenvy.blueprints.blueprint_helpers import inject_blueprints_list_into_main_scene, remove_blueprints_list_from_main_scene
from ..constants import TEMPSCENE_PREFIX
from ..common.generate_temporary_scene_and_export import generate_temporary_scene_and_export, copy_hollowed_collection_into, clear_hollow_scene
from ..common.export_gltf import (generate_gltf_export_settings, export_gltf)
from .is_object_dynamic import is_object_dynamic, is_object_static

def assets_to_fake_ron(list_like):
    result = []
    for item in list_like:
        result.append(f"(name: \"{item['name']}\", path: \"{item['path']}\")")
    return f"({result})".replace("'", '')#.join(", ")
        

def export_main_scene(scene, settings, blueprints_data): 
    gltf_export_settings = generate_gltf_export_settings(settings)
    assets_path_full = getattr(settings,"assets_path_full")
    levels_path_full = getattr(settings,"levels_path_full")

    export_blueprints = getattr(settings.auto_export,"export_blueprints")
    export_separate_dynamic_and_static_objects = getattr(settings.auto_export, "export_separate_dynamic_and_static_objects")

    gltf_export_settings = { **gltf_export_settings, 
                       'use_active_scene': True, 
                       'use_active_collection':True, 
                       'use_active_collection_with_nested':True,  
                       'use_visible': False,
                       'use_renderable': False,
                       'export_apply':True
                       }

    if export_blueprints : 
        gltf_output_path = os.path.join(levels_path_full, scene.name)

        inject_blueprints_list_into_main_scene(scene, blueprints_data, settings)
        print("main scene", scene)
        for asset in scene.user_assets:
            print("  user asset", asset.name, asset.path)
        for asset in scene.generated_assets:
            print("  generated asset", asset)
        """for blueprint in blueprints_data.blueprints_per_scenes[scene.name]:
            print("BLUEPRINT", blueprint)"""
        blueprint_instances_in_scene = blueprints_data.blueprint_instances_per_main_scene.get(scene.name, {}).keys()
        blueprints_in_scene = [blueprints_data.blueprints_per_name[blueprint_name] for blueprint_name in blueprint_instances_in_scene]
        #yala = [blueprint.collection.user_assets for blueprint in blueprints_in_scene]
        #print("dsfsdf", yala)
        auto_assets = []

        all_assets = []
        export_gltf_extension = getattr(settings.auto_export, "export_gltf_extension", ".glb")

        blueprints_path =  getattr(settings, "blueprints_path")
        for blueprint in blueprints_in_scene:
            if blueprint.local:
                blueprint_exported_path = os.path.join(blueprints_path, f"{blueprint.name}{export_gltf_extension}")
            else:
                # get the injected path of the external blueprints
                blueprint_exported_path = blueprint.collection['export_path'] if 'export_path' in blueprint.collection else None
            if blueprint_exported_path is not None: # and not does_asset_exist(assets_list, blueprint_exported_path):
                auto_assets.append({"name": blueprint.name, "path": blueprint_exported_path})#, "generated": True, "internal":blueprint.local, "parent": None})

            # now also add the assets of the blueprints # TODO: wait no , these should not be a part of the (scene) local assets
            for asset in blueprint.collection.user_assets:
                print("adding assets of blueprint", asset.name)
                all_assets.append({"name": asset.name, "path": asset.path})

        """for asset in auto_assets:
            print("  generated asset", asset.name, asset.path)"""
        
        materials_path =  getattr(settings, "materials_path")
        current_project_name = Path(bpy.context.blend_data.filepath).stem
        materials_library_name = f"{current_project_name}_materials"
        materials_exported_path = os.path.join(materials_path, f"{materials_library_name}{export_gltf_extension}")
        material_assets = [{"name": materials_library_name, "path": materials_exported_path}] # we also add the material library as an asset

        scene["BlenvyAssets"] = assets_to_fake_ron(all_assets + [{"name": asset.name, "path": asset.path} for asset in scene.user_assets] + auto_assets + material_assets)
        #scene["BlenvyAssets"] = assets_to_fake_ron([{'name':'foo', 'path':'bar'}])

        if export_separate_dynamic_and_static_objects:
            #print("SPLIT STATIC AND DYNAMIC")
            # first export static objects
            generate_temporary_scene_and_export(
                settings, 
                temp_scene_name=TEMPSCENE_PREFIX,
                additional_data = scene,
                gltf_export_settings=gltf_export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(scene.collection, temp_collection, blueprints_data=blueprints_data, filter=is_object_static, settings=settings),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=scene.collection, temp_scene=temp_scene, **params)
            )

            # then export all dynamic objects
            gltf_output_path = os.path.join(levels_path_full, scene.name+ "_dynamic")
            generate_temporary_scene_and_export(
                settings, 
                temp_scene_name=TEMPSCENE_PREFIX,
                additional_data = scene,
                gltf_export_settings=gltf_export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(scene.collection, temp_collection, blueprints_data=blueprints_data, filter=is_object_dynamic, settings=settings),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=scene.collection, temp_scene=temp_scene, **params)
            )

        else:
            #print("NO SPLIT")
            generate_temporary_scene_and_export(
                settings, 
                temp_scene_name=TEMPSCENE_PREFIX,
                additional_data = scene,
                gltf_export_settings=gltf_export_settings,
                gltf_output_path=gltf_output_path,
                tempScene_filler= lambda temp_collection: copy_hollowed_collection_into(scene.collection, temp_collection, blueprints_data=blueprints_data, settings=settings),
                tempScene_cleaner= lambda temp_scene, params: clear_hollow_scene(original_root_collection=scene.collection, temp_scene=temp_scene, **params)
            )

        remove_blueprints_list_from_main_scene(scene)

    else:
        gltf_output_path = os.path.join(assets_path_full, scene.name)
        print("       exporting gltf to", gltf_output_path, ".gltf/glb")
        if settings.auto_export.dry_run == "DISABLED":
            export_gltf(gltf_output_path, gltf_export_settings)




