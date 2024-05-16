import json

def get_user_assets(scene_or_collection):
    user_assets = getattr(scene_or_collection, 'user_assets', [])
    return user_assets

def get_generated_assets(scene_or_collection):
    generated_assets = []
    return generated_assets

def get_user_assets_as_list(scene_or_collection):
    raw = get_user_assets(scene_or_collection)
    result = []
    for asset in raw:
        result.append({"name": asset.name, "path": asset.path, "type": "MODEL", "internal": False, "parent": None})
    return result

def upsert_asset(scene_or_collection, asset):
    new_asset = scene_or_collection.user_assets.add()
    new_asset.name = asset["name"]
    new_asset.path = asset["path"]

def remove_asset(scene_or_collection, asset):
    scene_or_collection.user_assets.remove(scene_or_collection.user_assets.find(asset["path"]))

def does_asset_exist(scene_or_collection, ref_asset):
    user_assets = getattr(scene_or_collection, 'user_assets', [])
    in_list = [asset for asset in user_assets if (asset.path == ref_asset["path"])]
    in_list = len(in_list) > 0
    return in_list