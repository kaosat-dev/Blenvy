import os
import bpy
from pathlib import Path
from ..core.helpers_collections import (traverse_tree)

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
        # TODO: do NOT modify objects like this !! do it in a different function
        object['MaterialInfo'] = '(name: "'+material.name+'", source: "'+current_project_name + '")' 

    return used_materials_names


def get_all_materials(collection_names, library_scenes): 
    used_material_names = []
    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                for object in cur_collection.all_objects:
                    used_material_names = used_material_names + get_materials(object)

    # we only want unique names
    used_material_names = list(set(used_material_names))
    return used_material_names