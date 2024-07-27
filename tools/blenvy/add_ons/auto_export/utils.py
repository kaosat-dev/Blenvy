import posixpath
import bpy
from pathlib import Path
from blenvy.assets.assets_scan import get_blueprint_asset_tree, get_level_scene_assets_tree2
from blenvy.add_ons.bevy_components.utils import is_component_valid_and_enabled
from .constants import custom_properties_to_filter_out

def remove_unwanted_custom_properties(object):
    to_remove = []
    component_names = list(object.keys()) # to avoid 'IDPropertyGroup changed size during iteration' issues
    for component_name in component_names:
        if not is_component_valid_and_enabled(object, component_name):
            to_remove.append(component_name)
    for cp in custom_properties_to_filter_out + to_remove:
        if cp in object:
            del object[cp]

def assets_to_fake_ron(list_like):
    result = []
    for item in list_like:
        result.append(f"(name: \"{item['name']}\", path: \"{item['path']}\")")

    return f"(assets: {result})".replace("'", '')

# TODO : move to assets
def upsert_scene_assets(scene, blueprints_data, settings):
    all_assets = []
    all_assets_raw = get_level_scene_assets_tree2(level_scene=scene, blueprints_data=blueprints_data, settings=settings)
    local_assets =  [{"name": asset["name"], "path": asset["path"]} for asset in all_assets_raw if asset['parent'] is None and asset["path"] != "" ] 
    all_assets = [{"name": asset["name"], "path": asset["path"]} for asset in all_assets_raw if asset["path"] != "" ] 
    print("all_assets_raw", all_assets_raw)
    print("all_assets", all_assets)
    print("local assets", local_assets)
    scene["BlueprintAssets"] = assets_to_fake_ron(all_assets) #local_assets

def upsert_blueprint_assets(blueprint, blueprints_data, settings):   
    all_assets_raw = get_blueprint_asset_tree(blueprint=blueprint, blueprints_data=blueprints_data, settings=settings)
   
    all_assets = []
    auto_assets = []
    local_assets =  [{"name": asset["name"], "path": asset["path"]} for asset in all_assets_raw if asset['parent'] is None and asset["path"] != "" ]
    print("all_assets_raw", all_assets_raw)
    print("local assets", local_assets)
    blueprint.collection["BlueprintAssets"] = assets_to_fake_ron(local_assets)
