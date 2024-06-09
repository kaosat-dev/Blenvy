import os
import bpy
from pathlib import Path
from ..core.helpers_collections import (traverse_tree)

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
    export_gltf_extension = getattr(settings.auto_export, "export_gltf_extension", ".glb")

    current_project_name = Path(bpy.context.blend_data.filepath).stem
    materials_library_name = f"{current_project_name}_materials"
    materials_exported_path = os.path.join(materials_path, f"{materials_library_name}{export_gltf_extension}")
    for object in materials_per_object.keys():
        material = materials_per_object[object]
        # TODO: switch to using actual components ?
        materials_exported_path = os.path.join(materials_path, f"{materials_library_name}{export_gltf_extension}")
        object['MaterialInfo'] = f'(name: "{material.name}", path: "{materials_exported_path}")' 