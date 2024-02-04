import os
import bmesh
import bpy
import mathutils

#####################################################
#### Helpers ####

# Makes an empty, at location, stores it in existing collection, from https://blender.stackexchange.com/questions/51290/how-to-add-empty-object-not-using-bpy-ops
def make_empty(name, location, coll_name): #string, vector, string of existing coll
    empty_obj = bpy.data.objects.new( "empty", None, )
    empty_obj.name = name
    empty_obj.empty_display_size = 1 
    bpy.data.collections[coll_name].objects.link(empty_obj)
    empty_obj.location = location
    return empty_obj

# Makes an empty, at the specified location, rotation, scale stores it in existing collection, from https://blender.stackexchange.com/questions/51290/how-to-add-empty-object-not-using-bpy-ops
def make_empty2(name, location, rotation, scale, collection):
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

def make_cube(name, location=[0,0,0], rotation=[0,0,0], scale=[1,1,1], collection=None):
    new_mesh = bpy.data.meshes.new(name+"_Mesh") #None
    """verts = [( 1.0,  1.0,  0.0), 
         ( 1.0, -1.0,  0.0),
         (-1.0, -1.0,  0.0),
         (-1.0,  1.0,  0.0),
         ]  # 4 verts made with XYZ coords
    edges = []
    faces = [[0, 1, 2, 3]]
    new_mesh.from_pydata(verts, edges, faces)"""


    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=0.1, matrix=mathutils.Matrix.Translation(location)) # FIXME: other ways to set position seems to fail ?
    bm.to_mesh(new_mesh)
    bm.free()

    new_object = bpy.data.objects.new(name, new_mesh)
    new_object.name = name
    new_object.location = location
    new_object.scale = scale
    new_object.rotation_euler = rotation

    if collection != None:
        collection.objects.link( new_object )
    return new_object


def make_empty3(name, location, rotation, scale, collection): 
    original_active_object = bpy.context.active_object
    print("original_active_object", original_active_object)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location, rotation=rotation, scale=scale)
    empty_obj = bpy.context.active_object
    print("empty obj", name, empty_obj, bpy.context.object)
    empty_obj.name = name
    empty_obj.scale = scale # scale is not set correctly ?????
    bpy.context.view_layer.objects.active = original_active_object
    return empty_obj

# traverse all collections
def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

def check_if_blueprints_exist(collections, folder_path, extension):
    not_found_blueprints = []
    for collection_name in collections:
        gltf_output_path = os.path.join(folder_path, collection_name + extension)
        # print("gltf_output_path", gltf_output_path)
        found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
        if not found:
            not_found_blueprints.append(collection_name)
    return not_found_blueprints


def check_if_blueprint_on_disk(scene_name, folder_path, extension):
    gltf_output_path = os.path.join(folder_path, scene_name + extension)
    found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
    print("level", scene_name, "found", found, "path", gltf_output_path)
    return found

