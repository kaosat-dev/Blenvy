import posixpath
import bpy
from pathlib import Path
from blenvy.assets.assets_scan import get_blueprint_asset_tree, get_level_scene_assets_tree2

def assets_to_fake_ron(list_like):
    result = []
    for item in list_like:
        result.append(f"(name: \"{item['name']}\", path: \"{item['path']}\")")

    return f"(assets: {result})".replace("'", '')

# TODO : move to assets
def upsert_scene_assets(scene, blueprints_data, settings):
    """print("level scene", scene)
    for asset in scene.user_assets:
        print("  user asset", asset.name, asset.path)
    for asset in scene.generated_assets:
        print("  generated asset", asset)"""
    """for blueprint in blueprints_data.blueprints_per_scenes[scene.name]:
        print("BLUEPRINT", blueprint)"""
    blueprint_instances_in_scene = blueprints_data.blueprint_instances_per_level_scene.get(scene.name, {}).keys()
    blueprints_in_scene = [blueprints_data.blueprints_per_name[blueprint_name] for blueprint_name in blueprint_instances_in_scene]
    #yala = [blueprint.collection.user_assets for blueprint in blueprints_in_scene]
    #print("dsfsdf", yala)
    level_assets = []
    all_assets = []
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")

    blueprints_path =  getattr(settings, "blueprints_path")
    for blueprint in blueprints_in_scene:
        if blueprint.local:
            blueprint_exported_path = posixpath.join(blueprints_path, f"{blueprint.name}{export_gltf_extension}")
        else:
            # get the injected path of the external blueprints
            blueprint_exported_path = blueprint.collection['export_path'] if 'export_path' in blueprint.collection else None
            # add their material path
            materials_exported_path = blueprint.collection['materials_path'] if 'materials_path' in blueprint.collection else None
            level_assets.append({"name": blueprint.name+"_material", "path": materials_exported_path})#, "generated": True, "internal":blueprint.local, "parent": None})


        if blueprint_exported_path is not None: # and not does_asset_exist(assets_list, blueprint_exported_path):
            level_assets.append({"name": blueprint.name, "path": blueprint_exported_path})#, "generated": True, "internal":blueprint.local, "parent": None})

        # now also add the assets of the blueprints # TODO: wait no , these should not be a part of the (scene) local assets
        for asset in blueprint.collection.user_assets:
            #print("adding assets of blueprint", asset.name)
            all_assets.append({"name": asset.name, "path": asset.path})

    """for asset in level_assets:
        print("  generated asset", asset.name, asset.path)"""
    
    materials_path =  getattr(settings, "materials_path")
    current_project_name = Path(bpy.context.blend_data.filepath).stem
    materials_library_name = f"{current_project_name}_materials"
    materials_exported_path = posixpath.join(materials_path, f"{materials_library_name}{export_gltf_extension}")
    material_assets = [{"name": materials_library_name, "path": materials_exported_path}] # we also add the material library as an asset
    print("material_assets", material_assets, "extension", export_gltf_extension)


    all_assets_raw = get_level_scene_assets_tree2(level_scene=scene, blueprints_data=blueprints_data, settings=settings)
    local_assets =  [{"name": asset["name"], "path": asset["path"]} for asset in all_assets_raw if asset['parent'] is None and asset["path"] != "" ] 
    all_assets = [{"name": asset["name"], "path": asset["path"]} for asset in all_assets_raw if asset["path"] != "" ] 
    print("all_assets_raw", all_assets_raw)
    print("all_assets", all_assets)
    print("local assets", local_assets + material_assets)
    scene["BlueprintAssets"] = assets_to_fake_ron(local_assets + material_assets)


    #scene["BlueprintAssets"] = assets_to_fake_ron(all_assets + [{"name": asset.name, "path": asset.path} for asset in scene.user_assets] + level_assets + material_assets)
    #scene["BlueprintAssets"] = assets_to_fake_ron([{'name':'foo', 'path':'bar'}])

def upsert_blueprint_assets(blueprint, blueprints_data, settings):   
    all_assets_raw = get_blueprint_asset_tree(blueprint=blueprint, blueprints_data=blueprints_data, settings=settings)
   
    all_assets = []
    auto_assets = []
    local_assets =  [{"name": asset["name"], "path": asset["path"]} for asset in all_assets_raw if asset['parent'] is None and asset["path"] != "" ]
    print("all_assets_raw", all_assets_raw)
    print("local assets", local_assets)
    blueprint.collection["BlueprintAssets"] = assets_to_fake_ron(local_assets)
