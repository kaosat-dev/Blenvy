
from .helpers_export import export_gltf, generate_gltf_export_preferences
from .helpers import traverse_tree
import bpy
import os
from pathlib import Path

# get materials per object, and injects the materialInfo component
def get_materials(object):
    material_slots = object.material_slots
    used_materials_names = []
    #materials_per_object = {}
    current_project_name = Path(bpy.context.blend_data.filepath).stem

    for m in material_slots:
        material = m.material
        # print("    slot", m, "material", material)
        used_materials_names.append(material.name)
        # TODO:, also respect slots & export multiple materials if applicable ! 
        object['MaterialInfo'] = '(name: "'+material.name+'", source: "'+current_project_name + '")' 

    return used_materials_names

def clear_material_info(collection_names, library_scenes):
    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                for object in cur_collection.all_objects:
                    if 'MaterialInfo' in dict(object): # FIXME: hasattr does not work ????
                        del object["MaterialInfo"]
                   

def get_all_materials(collection_names, library_scenes): 
    #print("collecton", layerColl, "otot", layerColl.all_objects) #all_objects
    used_material_names = []
    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                #print("collection: ", cur_collection.name)
                for object in cur_collection.all_objects:
                    # print("  object:", object.name)
                    used_material_names = used_material_names + get_materials(object)
    # we only want unique names
    used_material_names = list(set(used_material_names))
    return used_material_names


def make_material_object(name, location, rotation, scale, material): 
    original_active_object = bpy.context.active_object
    # bpy.ops.object.empty_add(type='PLAIN_AXES', location=location, rotation=rotation, scale=scale)
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=location)  
    object = bpy.context.active_object
    object.name = name
    #obj.scale = scale # scale is not set correctly ?????
    if object.data.materials:
        # assign to 1st material slot
        object.data.materials[0] = material
    else:
        # no slots
        object.data.materials.append(material)

    bpy.context.view_layer.objects.active = original_active_object
    return object


# generates a materials scene: 
def generate_materials_scenes(used_material_names):
    temp_scene = bpy.data.scenes.new(name="__materials_scene")
    bpy.context.window.scene = temp_scene

    for index, material_name in enumerate(used_material_names):
        material = bpy.data.materials[material_name]
        make_material_object("Material_"+material_name, [index * 0.2,0,0], [], [], material)

    # we set our active scene to be this one : this is needed otherwise the stand-in objects get generated in the wrong scene
    return temp_scene

def clear_materials_scene(temp_scene):
    root_collection = temp_scene.collection 
    scene_objects = [o for o in root_collection.objects]
    for object in scene_objects:
        bpy.data.objects.remove(object, do_unlink=True)
    bpy.data.scenes.remove(temp_scene)

# exports the materials used inside the current project:
# the name of the output path is <materials_folder>/<name_of_your_blend_file>_materials_library.gltf/glb
def export_materials(collections, library_scenes, folder_path, addon_prefs):
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    export_materials_path = getattr(addon_prefs,"export_materials_path")

    used_material_names = get_all_materials(collections, library_scenes)
    current_project_name = Path(bpy.context.blend_data.filepath).stem

    print("materials", used_material_names)

    # save the current active scene
    current_scene = bpy.context.window.scene
    mat_scene = generate_materials_scenes(used_material_names)


    gltf_output_path = os.path.join(folder_path, export_materials_path, current_project_name + "_materials_library")
    print("       exporting Materials to", gltf_output_path, ".gltf/glb")
    export_settings = { **gltf_export_preferences, 
                    'use_active_scene': True, 
                    'use_active_collection':True, 
                    'use_active_collection_with_nested':True,  
                    'use_visible': False,
                    'use_renderable': False,
                    'export_apply':True
                    }
    export_gltf(gltf_output_path, export_settings)

    # remove materials scenes
    clear_materials_scene(mat_scene)

    # reset scene to previously selected scene
    bpy.context.window.scene = current_scene

def cleanup_materials(collections, library_scenes):
    # remove temporary components
    clear_material_info(collections, library_scenes)