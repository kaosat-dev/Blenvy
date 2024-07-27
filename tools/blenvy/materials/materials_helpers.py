import os
import posixpath
from ..core.helpers_collections import (traverse_tree)

def find_materials_not_on_disk(materials, materials_path_full, extension):
    not_found_materials = []
    for material in materials:
        gltf_output_path = os.path.join(materials_path_full, material.name + extension)
        # print("gltf_output_path", gltf_output_path)
        found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
        if not found:
            not_found_materials.append(material)
    return not_found_materials

def check_if_material_on_disk(scene_name, folder_path, extension):
    gltf_output_path = os.path.join(folder_path, scene_name + extension)
    found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
    return found

# get materials per object, and injects the materialInfo component
def get_materials(object, materials_per_object):
    material_slots = object.material_slots
    used_materials_names = []

    for m in material_slots:
        material = m.material
        # print("    slot", m, "material", material)
        used_materials_names.append(material.name)
        # TODO:, also respect slots & export multiple materials if applicable ! 
        if not object in materials_per_object:
            materials_per_object[object] = []
        materials_per_object[object].append(material)
    return used_materials_names


def get_all_materials(collection_names, library_scenes): 
    used_material_names = []
    materials_per_object = {}

    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                for object in cur_collection.all_objects:
                    used_material_names = used_material_names + get_materials(object, materials_per_object)

    # we only want unique names
    used_material_names = list(set(used_material_names))
    return (used_material_names, materials_per_object)

def add_material_info_to_objects(materials_per_object, settings):
    materials_path =  getattr(settings, "materials_path")
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")
    for object in materials_per_object.keys():
        material_infos = []
        for material in materials_per_object[object]:
            materials_exported_path = posixpath.join(materials_path, f"{material.name}{export_gltf_extension}")
            material_info = f'(name: "{material.name}", path: "{materials_exported_path}")' 
            material_infos.append(material_info)
        # problem with using actual components: you NEED the type registry/component infos, so if there is none , or it is not loaded yet, it does not work
        # for a few components we could hardcode this
        #bpy.ops.blenvy.component_add(target_item_name=object.name, target_item_type="OBJECT", component_type="blenvy::blueprints::materials::MaterialInfos", component_value=component_value)
        object['MaterialInfos'] = f"({material_infos})".replace("'","") 
        print("adding materialInfos to object", object, "material infos", material_infos)


# get all the materials of all objects in a given scene
def get_scene_materials(scene):
    used_material_names = []
    materials_per_object = {}

    root_collection = scene.collection
    for cur_collection in traverse_tree(root_collection):
        for object in cur_collection.all_objects:
            used_material_names = used_material_names + get_materials(object, materials_per_object)

    # we only want unique names
    used_material_names = list(set(used_material_names))
    return (used_material_names, materials_per_object)

# get all the materials of all objects used by a given blueprint
def get_blueprint_materials(blueprint):
    materials_per_object = {}
    used_material_names = []

    for object in blueprint.collection.all_objects:
        used_material_names = used_material_names + get_materials(object, materials_per_object)
    
    # we only want unique names
    used_material_names = list(set(used_material_names))
    return (used_material_names, materials_per_object)
