import json

def get_assets(scene_or_collection):
    assets = json.loads(scene_or_collection.get('assets')) if 'assets' in scene_or_collection else []
    return assets
