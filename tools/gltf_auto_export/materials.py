
from .helpers import traverse_tree


def get_materials(object):
    material_slots = object.material_slots
    used_materials_names = []
    materials_per_object = {}
    for m in material_slots:
        material = m.material
        print("    slot", m, "material", material)
        used_materials_names.append(material.name)
        # meh, also respect slots ! 
        object["MaterialInfo"] = '"'+material.name+'"' 
        # del object["material_info"]
    return used_materials_names


def get_all_materials(collection_names, library_scenes): 
    #print("collecton", layerColl, "otot", layerColl.all_objects) #all_objects
    used_materials_names = []
    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                print("collection: ", cur_collection.name)
                for object in cur_collection.all_objects:
                    print("  object:", object.name)
                    used_materials_names = used_materials_names + get_materials(object)
    
    return used_materials_names
                