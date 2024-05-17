import json
import bpy

def upsert_settings(name, data):
    stored_settings = bpy.data.texts[name] if name in bpy.data.texts else None#bpy.data.texts.new(name)
    if stored_settings is None:
        stored_settings = bpy.data.texts.new(name)
        stored_settings.write(json.dumps(data))
    else:
        current_settings = json.loads(stored_settings.as_string())
        current_settings = {**current_settings, **data}
        stored_settings.clear()
        stored_settings.write(json.dumps(current_settings))

def load_settings(name):
    stored_settings = bpy.data.texts[name] if name in bpy.data.texts else None
    if stored_settings != None:
        return json.loads(stored_settings.as_string())
    return None

# checks if old & new settings (dicts really) are identical
def are_settings_identical(old, new, white_list=None):
    if old is None and new is None:
        return True
    if old is None and new is not None:
        return False
    if old is not None and new is None:
        return False
    
    old_items = sorted(old.items())
    new_items = sorted(new.items())
    if white_list is not None:
        old_items_override = {}
        new_items_override = {}
        for key in white_list:
            if key in old_items:
                old_items_override[key] = old_items[key]
            if key in new_items:
                new_items_override[key] = new_items[key]
        old_items = old_items_override
        new_items = new_items_override
            
    return old_items != new_items if new is not None else False