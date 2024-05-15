import json

def get_assets(scene_or_collection):
    assets = json.loads(scene_or_collection.get('assets')) if 'assets' in scene_or_collection else []
    return assets

def does_asset_exist(assets, asset_path):
    in_list = [asset for asset in assets if (asset["path"] == asset_path)]
    in_list = len(in_list) > 0
    return in_list