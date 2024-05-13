import json
import bpy

def upsert_settings(name, data):
    stored_settings = bpy.data.texts[name] if name in bpy.data.texts else bpy.data.texts.new(name)
    stored_settings.clear()
    stored_settings.write(json.dumps(data))

def load_settings(name):
    stored_settings = bpy.data.texts[name] if name in bpy.data.texts else None
    if stored_settings != None:
        return json.loads(stored_settings.as_string())
    return None
