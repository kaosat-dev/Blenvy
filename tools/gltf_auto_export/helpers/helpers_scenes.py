import bpy
from .helpers_collections import (set_active_collection)
from .object_makers import (make_empty)

# copies the contents of a collection into another one while replacing library instances with empties
def copy_hollowed_collection_into(source_collection, destination_collection, parent_empty=None, filter=None, collection_instances_combine_mode=None, library_collections=[]):
    root_objects = []
    special_properties= { # to be able to reset any special property afterwards
        "combine": [],
    }
    for object in source_collection.objects:
        if filter is not None and filter(object) is False:
            continue
        #check if a specific collection instance does not have an ovveride for combine_mode
        combine_mode = object['_combine'] if '_combine' in object else collection_instances_combine_mode

        if object.instance_type == 'COLLECTION' and (combine_mode == 'Split' or (combine_mode == 'EmbedExternal' and (object.instance_collection.name in library_collections)) ): 
            #print("creating empty for", object.name, object.instance_collection.name, library_collections, combine_mode)
            collection_name = object.instance_collection.name
            original_name = object.name

            object.name = original_name + "____bak"
            empty_obj = make_empty(original_name, object.location, object.rotation_euler, object.scale, destination_collection)
            """we inject the collection/blueprint name, as a component called 'BlueprintName', but we only do this in the empty, not the original object"""
            empty_obj['BlueprintName'] = '"'+collection_name+'"'
            empty_obj['SpawnHere'] = ''

            for k, v in object.items():
                if k != 'template' or k != '_combine': # do not copy these properties
                    empty_obj[k] = v
            if parent_empty is not None:
                empty_obj.parent = parent_empty
        else:
            # we backup special properties that we do not want to export, and remove them
            if '_combine' in object:
                special_properties["combine"].append((object, object['_combine']))
                del object['_combine']

            if parent_empty is not None:
                object.parent = parent_empty
                destination_collection.objects.link(object)
            else:
                root_objects.append(object)
                destination_collection.objects.link(object)

    # for every sub-collection of the source, copy its content into a new sub-collection of the destination
    for collection in source_collection.children:
        original_name = collection.name
        collection.name = original_name + "____bak"
        collection_placeholder = make_empty(original_name, [0,0,0], [0,0,0], [1,1,1], destination_collection)

        if parent_empty is not None:
            collection_placeholder.parent = parent_empty

        nested_results = copy_hollowed_collection_into(collection, destination_collection, collection_placeholder, filter, collection_instances_combine_mode, library_collections)
        sub_root_objects = nested_results["root_objects"]
        sub_special_properties = nested_results["special_properties"]

        root_objects.extend(sub_root_objects)
        for s in sub_special_properties.keys():
            if not s in special_properties.keys():
                special_properties[s] = []
            special_properties[s].extend(sub_special_properties[s])

    return {"root_objects": root_objects, "special_properties": special_properties}

# clear & remove "hollow scene"
def clear_hollow_scene(temp_scene, original_root_collection, root_objects, special_properties):
    def restore_original_names(collection):
        if collection.name.endswith("____bak"):
            collection.name = collection.name.replace("____bak", "")
        for object in collection.objects:
            if object.instance_type == 'COLLECTION':
                if object.name.endswith("____bak"):
                    object.name = object.name.replace("____bak", "")
        for child_collection in collection.children:
            restore_original_names(child_collection)
    
    # reset original names
    restore_original_names(original_root_collection)

    # remove empties (only needed when we go via ops ????)
    temp_root_collection = temp_scene.collection 
    temp_scene_objects = [o for o in temp_root_collection.objects]
    for object in temp_scene_objects:
        if object.type == 'EMPTY':
            if hasattr(object, "SpawnHere"):
                bpy.data.objects.remove(object, do_unlink=True)
            else:
                try: 
                    temp_root_collection.objects.unlink(object)
                except:
                    print("failed to unlink", object)
                if object in root_objects:
                    pass
                else:
                    bpy.data.objects.remove(object, do_unlink=True)
        else:
            temp_root_collection.objects.unlink(object)

    # remove temporary collections
    """for collection in temporary_collections:
        bpy.data.collections.remove(collection)"""

    # put back special properties
    for (object, value) in special_properties["combine"]:
        object['_combine'] = value

    # remove the temporary scene
    bpy.data.scenes.remove(temp_scene)


# convenience utility to get lists of scenes
def get_scenes(addon_prefs):
    level_scene_names= list(map(lambda scene: scene.name, getattr(addon_prefs,"main_scenes")))
    library_scene_names = list(map(lambda scene: scene.name, getattr(addon_prefs,"library_scenes")))

    level_scene_names = list(filter(lambda name: name in bpy.data.scenes, level_scene_names))
    library_scene_names = list(filter(lambda name: name in bpy.data.scenes, library_scene_names))

    level_scenes = list(map(lambda name: bpy.data.scenes[name], level_scene_names))
    library_scenes = list(map(lambda name: bpy.data.scenes[name], library_scene_names))
    
    return [level_scene_names, level_scenes, library_scene_names, library_scenes]


