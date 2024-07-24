import os
import posixpath
import bpy
from pathlib import Path

from ..core.helpers_collections import (traverse_tree)

def find_materials_not_on_disk(materials, materials_path_full, extension):
    not_found_materials = []

    current_project_name = Path(bpy.context.blend_data.filepath).stem
    materials_library_name = f"{current_project_name}_materials"
    materials_exported_path = os.path.join(materials_path_full, f"{materials_library_name}{extension}")

    found = os.path.exists(materials_exported_path) and os.path.isfile(materials_exported_path)
    for material in materials:
        if not found:
                not_found_materials.append(material)

    """for material in materials:
        gltf_output_path = os.path.join(materials_path_full, material.name + extension)
        # print("gltf_output_path", gltf_output_path)
        found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
        if not found:
            not_found_materials.append(material)"""
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
        materials_per_object[object] = material
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

    current_project_name = Path(bpy.context.blend_data.filepath).stem
    materials_library_name = f"{current_project_name}_materials"
    materials_exported_path = posixpath.join(materials_path, f"{materials_library_name}{export_gltf_extension}")
    #print("ADDING MAERIAL INFOS")
    for object in materials_per_object.keys():
        material = materials_per_object[object]

        # problem with using actual components: you NEED the type registry/component infos, so if there is none , or it is not loaded yet, it does not work
        # for a few components we could hardcode this
        component_value = f'(name: "{material.name}", path: "{materials_exported_path}")' 
        #bpy.ops.blenvy.component_add(target_item_name=object.name, target_item_type="OBJECT", component_type="blenvy::blueprints::materials::MaterialInfo", component_value=component_value)

        materials_exported_path = posixpath.join(materials_path, f"{materials_library_name}{export_gltf_extension}")
        object['MaterialInfo'] = component_value
        print("adding materialInfo to object", object, "material info", component_value)


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
