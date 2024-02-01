import bpy
from .helpers_collections import (find_layer_collection_recursive)
from .helpers import (make_empty2)

def generate_blueprint_hollow_scene(blueprint_collection, library_collections, addon_prefs):
    collection_instances_combine_mode = getattr(addon_prefs, "collection_instances_combine_mode")

    temp_scene = bpy.data.scenes.new(name="temp_scene_"+blueprint_collection.name)
    temp_scene_root_collection = temp_scene.collection

    # we set our active scene to be this one : this is needed otherwise the stand-in empties get generated in the wrong scene
    bpy.context.window.scene = temp_scene
    found = find_layer_collection_recursive(temp_scene_root_collection, bpy.context.view_layer.layer_collection)
    if found:
        # once it's found, set the active layer collection to the one we found
        bpy.context.view_layer.active_layer_collection = found

    original_names = []
    temporary_collections = []
    root_objects = []
    special_properties= { # to be able to reset any special property afterwards
        "combine": [],
    }

    # TODO also add the handling for "template" flags, so that instead of creating empties we link the data from the sub collection INTO the parent collection
    # copies the contents of a collection into another one while replacing blueprint instances with empties
    # if we have combine_mode set to "Inject", we take all the custom attributed of the nested (1 level only ! unless we use 'deepMerge') custom attributes and copy them to this level 
    def copy_hollowed_collection_into(source_collection, destination_collection, parent_empty=None):
        for object in source_collection.objects:
            combine_mode = object['_combine'] if '_combine' in object else collection_instances_combine_mode

            if object.instance_type == 'COLLECTION' and (combine_mode == 'Split' or (combine_mode == 'EmbedExternal' and (object.instance_collection.name in library_collections)) ): 

                # get the name of the collection this is an instance of
                collection_name = object.instance_collection.name
                """
                blueprint_template = object['Template'] if 'Template' in object else False
                if blueprint_template and parent_empty is None: # ONLY WORKS AT ROOT LEVEL
                    print("BLUEPRINT TEMPLATE", blueprint_template, destination_collection, parent_empty)
                    for object in source_collection.objects:
                        if object.type == 'EMPTY' and object.name.endswith("components"):
                            original_collection = bpy.data.collections[collection_name]
                            components_holder = object
                            print("WE CAN INJECT into", object, "data from", original_collection)

                            # now we look for components inside the collection
                            components = {}
                            for object in original_collection.objects:
                                if object.type == 'EMPTY' and object.name.endswith("components"):
                                    for component_name in object.keys():
                                        if component_name not in '_RNA_UI':
                                            print( component_name , "-" , object[component_name] )
                                            components[component_name] = object[component_name]

                            # copy template components into target object
                            for key in components:
                                print("copying ", key,"to", components_holder)
                                if not key in components_holder:
                                    components_holder[key] = components[key]                            
                """

                original_name = object.name
                original_names.append(original_name)

                object.name = original_name + "____bak"
                empty_obj = make_empty2(original_name, object.location, object.rotation_euler, object.scale, destination_collection)
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
            collection_placeholder = make_empty2(original_name, [0,0,0], [0,0,0], [1,1,1], destination_collection)

            if parent_empty is not None:
                collection_placeholder.parent = parent_empty

            copy_hollowed_collection_into(collection, destination_collection, collection_placeholder)

            """
            copy_collection = bpy.data.collections.new(collection.name + "____collection_export")
            # save the newly created collection for later reuse
            temporary_collections.append(copy_collection)

            # copy & link objects
            copy_hollowed_collection_into(collection, copy_collection)
            destination_collection.children.link(copy_collection)"""

    copy_hollowed_collection_into(blueprint_collection, temp_scene_root_collection)

    return (temp_scene, temporary_collections, root_objects, special_properties)




# clear & remove "hollow scene"
def clear_blueprint_hollow_scene(temp_scene, original_collection, temporary_collections, root_objects, special_properties):

    def restore_original_names(collection):
        if collection.name.endswith("____bak"):
            collection.name = collection.name.replace("____bak", "")
        for object in collection.objects:
            if object.instance_type == 'COLLECTION':
                if object.name.endswith("____bak"):
                    object.name = object.name.replace("____bak", "")
        for child_collection in collection.children:
            restore_original_names(child_collection)
    
    restore_original_names(original_collection)

    # remove empties (only needed when we go via ops ????)
    temp_root_collection = temp_scene.collection 
    temp_scene_objects = [o for o in temp_root_collection.objects]
    for object in temp_scene_objects:
        if object.type == 'EMPTY':
            if hasattr(object, "SpawnHere"):
                bpy.data.objects.remove(object, do_unlink=True)
            else: 
                bpy.context.scene.collection.objects.unlink(object)
                if object in root_objects:
                    pass
                else:
                    bpy.data.objects.remove(object, do_unlink=True)
        else: 
            bpy.context.scene.collection.objects.unlink(object)

    # put back special properties
    for (object, value) in special_properties["combine"]:
        object['_combine'] = value

    # remove temporary collections
    for collection in temporary_collections:
        bpy.data.collections.remove(collection)

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
