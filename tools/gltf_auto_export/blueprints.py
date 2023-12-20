import bpy
from .helpers_collections import (find_layer_collection_recursive)
from .helpers import (make_empty3, traverse_tree)


def generate_blueprint_hollow_scene(blueprint_collection, library_collections):
    temp_scene = bpy.data.scenes.new(name="temp_scene_"+blueprint_collection.name)
    temp_scene_root_collection = temp_scene.collection

    # we set our active scene to be this one : this is needed otherwise the stand-in empties get generated in the wrong scene
    bpy.context.window.scene = temp_scene
    found = find_layer_collection_recursive(temp_scene_root_collection, bpy.context.view_layer.layer_collection)
    if found:
        # once it's found, set the active layer collection to the one we found
        bpy.context.view_layer.active_layer_collection = found

    original_names = []

    # TODO also add the handling for "template" flags, so that instead of creating empties we link the data from the sub collection INTO the parent collection
    # copies the contents of a collection into another one while replacing blueprint instances with empties
    def copy_hollowed_collection_into(source_collection, destination_collection):
        for object in source_collection.objects:
            flatten = 'Flatten' in object and object['Flatten'] == True # if the object has the "flatten" flag set to true, treat it as an embeded object and do not replace it with an empty
            # merge = 'Merge' in object and object['Merge'] == True 
            if object.instance_type == 'COLLECTION' and (object.instance_collection.name in library_collections) and not flatten:
                # if we have combine_mode set to "merge", we take all the custom attributed of the nested (1 level only ! unless we use 'deepMerge') custom attributes and copy them to this level 
                """TODO: implement later
                if merge:
                    foo = get_nested_components(object)
                    print("nested components", foo)
                    pass
                else: 
                """
                collection_name = object.instance_collection.name

                original_name = object.name
                original_names.append(original_name)

                object.name = original_name + "____bak"
                empty_obj = make_empty3(original_name, object.location, object.rotation_euler, object.scale, destination_collection)
                """we inject the collection/blueprint name, as a component called 'BlueprintName', but we only do this in the empty, not the original object"""
                empty_obj['BlueprintName'] = '"'+collection_name+'"'
                empty_obj['SpawnHere'] = ''

                for k, v in object.items():
                    empty_obj[k] = v
            else:
                destination_collection.objects.link(object)

        # for every sub-collection of the source, copy its content into a new sub-collection of the destination
        for collection in source_collection.children:
            copy_collection = bpy.data.collections.new(collection.name + "____collection_export")
            copy_hollowed_collection_into(collection, copy_collection)
            destination_collection.children.link(copy_collection)

    copy_hollowed_collection_into(blueprint_collection, temp_scene_root_collection)


    return (temp_scene, original_names)




# clear & remove "hollow scene"
def clear_blueprint_hollow_scene(temp_scene, original_collection, original_names):

    def restore_original_names(collection):
        for object in collection.objects:
            if object.instance_type == 'COLLECTION':
                if object.name.endswith("____bak"):
                    object.name = object.name.replace("____bak", "")
        for child_collection in collection.children:
            restore_original_names(child_collection)
    
    restore_original_names(original_collection)

    # remove empties (only needed when we go via ops ????)
    root_collection = temp_scene.collection 
    scene_objects = [o for o in root_collection.objects]
    for object in scene_objects:
        if object.type == 'EMPTY':
            if hasattr(object, "SpawnHere"):
                bpy.data.objects.remove(object, do_unlink=True)
            else: 
                bpy.context.scene.collection.objects.unlink(object)
            #bpy.data.objects.remove(object, do_unlink=True)

    bpy.data.scenes.remove(temp_scene)

# TODO : add a flag to also search of deeply nested components
def get_nested_components(object):
    if object.instance_type == 'COLLECTION':
        collection_name = object.instance_collection.name
        collection = bpy.data.collections[collection_name]
        all_objects = collection.all_objects
        result = []
        for object in all_objects:
            components = dict(object)
            if len(components.keys()) > 0:
                result += [(object, components)]
        return result
    return []
        #for collection in traverse_tree(collection):
        #    for object in collection.all_objects
