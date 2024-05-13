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
