import json
import bpy

def upsert_settings(name, data):
    stored_settings = bpy.data.texts[name] if name in bpy.data.texts else None
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
    if stored_settings is not None:
        try:
            return json.loads(stored_settings.as_string())
        except:
            return None
    return None


# given the input (actual) settings, filters out any invalid/useless params & params that are equal to defaults
def generate_complete_preferences_dict(settings, presets, ignore_list=[]):
    complete_preferences = {}    
    defaults = {}

    def filter_out(pair):
        key, value = pair
        if key in ignore_list:
            return False
        return True

    for k in presets.__annotations__:
        item = presets.__annotations__[k]
        default = item.keywords.get('default', None)
        defaults[k] = default
        #complete_preferences[k] = default
    # print("defaults", defaults)
    

    for key in list(settings.keys()):
        if key in defaults and settings[key] != defaults[key]: # only write out values different from defaults
            complete_preferences[key] = getattr(settings, key, None)
       
    print("complete_preferences", complete_preferences)

    """for key in list(settings.keys()):
        if key in defaults and settings[key] != defaults[key]: # only write out values different from defaults
            complete_preferences[key] = settings[key]"""

    complete_preferences = dict(filter(filter_out, dict(complete_preferences).items()))

    return complete_preferences


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