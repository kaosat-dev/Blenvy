import bpy
import json

# Makes an empty, at the specified location, rotation, scale stores it in existing collection, from https://blender.stackexchange.com/questions/51290/how-to-add-empty-object-not-using-bpy-ops
def make_empty(name, location, rotation, scale, collection):
    object_data = None 
    empty_obj = bpy.data.objects.new( name, object_data )
    
    empty_obj.empty_display_size = 2
    empty_obj.empty_display_type = 'PLAIN_AXES'   

    empty_obj.name = name
    empty_obj.location = location
    empty_obj.scale = scale
    empty_obj.rotation_euler = rotation

    collection.objects.link( empty_obj )
    #bpy.context.view_layer.update()
    return empty_obj

#".gltf_auto_export_settings"
def upsert_settings(name, data):
    stored_settings = bpy.data.texts[name] if name in bpy.data.texts else bpy.data.texts.new(name)
    stored_settings.clear()
    stored_settings.write(json.dumps(data))

def load_settings(name):
    stored_settings = bpy.data.texts[name] if name in bpy.data.texts else None
    if stored_settings != None:
        return json.loads(stored_settings.as_string())
    return None
