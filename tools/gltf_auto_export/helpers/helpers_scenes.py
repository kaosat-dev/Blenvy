import json
import bpy
from .helpers_collections import (CollectionNode, get_sub_collections, get_used_collections, set_active_collection)
from .object_makers import (make_empty)


# these are mostly for when using this add-on together with the bevy_components add-on
custom_properties_to_filter_out = ['_combine', 'template', 'components_meta']

def is_component_valid(object, component_name):
    if "components_meta" in object:
        target_components_metadata = object.components_meta.components
        component_meta = next(filter(lambda component: component["name"] == component_name, target_components_metadata), None)
        if component_meta != None:
            return component_meta.enabled and not component_meta.invalid
    return True

def remove_unwanted_custom_properties(object):
    to_remove = []
    for component_name in object.keys():
        if not is_component_valid(object, component_name):
            to_remove.append(component_name)
    
    for cp in custom_properties_to_filter_out + to_remove:
        if cp in object:
            del object[cp]

def duplicate_object(object):
    obj_copy = object.copy()
    if object.data:
        data = object.data.copy()
        obj_copy.data = data
    if object.animation_data and object.animation_data.action:
        obj_copy.animation_data.action = object.animation_data.action.copy()
    return obj_copy

#also removes unwanted custom_properties for all objects in hiearchy
def duplicate_object_recursive(object, parent, collection):
    original_name = object.name
    object.name = original_name + "____bak"
    copy = duplicate_object(object)
    copy.name = original_name
    collection.objects.link(copy)

    remove_unwanted_custom_properties(copy)

    if parent:
        copy.parent = parent

    for child in object.children:
        duplicate_object_recursive(child, copy, collection)
    return copy


# copies the contents of a collection into another one while replacing library instances with empties
def copy_hollowed_collection_into(source_collection, destination_collection, parent_empty=None, filter=None, library_collections=[], addon_prefs={}):
    collection_instances_combine_mode = getattr(addon_prefs, "collection_instances_combine_mode")
    legacy_mode = getattr(addon_prefs, "export_legacy_mode")
    collection_instances_combine_mode= collection_instances_combine_mode
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
            empty_obj['BlueprintName'] = '"'+collection_name+'"' if legacy_mode else '("'+collection_name+'")'
            empty_obj['SpawnHere'] = '()'

            # we also inject a list of all sub blueprints, so that the bevy side can preload them
            if not legacy_mode:
                root_node = CollectionNode()
                root_node.name = "root"
                children_per_collection = {}
                print("collection stuff", original_name)
                get_sub_collections([object.instance_collection], root_node, children_per_collection)
                empty_obj["BlueprintsList"] = f"({json.dumps(dict(children_per_collection))})"
                #empty_obj["Assets"] = {"Animations": [], "Materials": [], "Models":[], "Textures":[], "Audio":[], "Other":[]}
           

            # we copy custom properties over from our original object to our empty
            for component_name, component_value in object.items():
                if component_name not in custom_properties_to_filter_out and is_component_valid(object, component_name): #copy only valid properties
                    empty_obj[component_name] = component_value
            if parent_empty is not None:
                empty_obj.parent = parent_empty
        else:         
           
            # we create a copy of our object and its children, to leave the original one as it is
            if object.parent == None:
                copy = duplicate_object_recursive(object, None, destination_collection)

                if parent_empty is not None:
                    copy.parent = parent_empty                

    # for every sub-collection of the source, copy its content into a new sub-collection of the destination
    for collection in source_collection.children:
        original_name = collection.name
        collection.name = original_name + "____bak"
        collection_placeholder = make_empty(original_name, [0,0,0], [0,0,0], [1,1,1], destination_collection)

        if parent_empty is not None:
            collection_placeholder.parent = parent_empty

        copy_hollowed_collection_into(
            source_collection = collection, 
            destination_collection = destination_collection, 
            parent_empty = collection_placeholder, 
            filter = filter,
            library_collections = library_collections, 
            addon_prefs=addon_prefs
        )
    
    return {}

# clear & remove "hollow scene"
def clear_hollow_scene(temp_scene, original_root_collection):
    def restore_original_names(collection):
        if collection.name.endswith("____bak"):
            collection.name = collection.name.replace("____bak", "")
        for object in collection.objects:
            if object.instance_type == 'COLLECTION':
                if object.name.endswith("____bak"):
                    object.name = object.name.replace("____bak", "")
            else: 
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
        bpy.data.objects.remove(object, do_unlink=True)
    # remove the temporary scene
    bpy.data.scenes.remove(temp_scene)


# convenience utility to get lists of scenes
def get_scenes(addon_prefs):
    level_scene_names= list(map(lambda scene: scene.name, getattr(addon_prefs,"main_scenes"))) # getattr(addon_prefs, "main_scene_names_compact").split(',')#
    library_scene_names = list(map(lambda scene: scene.name, getattr(addon_prefs,"library_scenes"))) #getattr(addon_prefs, "main_scene_names_compact").split(',')#

    level_scene_names = list(filter(lambda name: name in bpy.data.scenes, level_scene_names))
    library_scene_names = list(filter(lambda name: name in bpy.data.scenes, library_scene_names))

    level_scenes = list(map(lambda name: bpy.data.scenes[name], level_scene_names))
    library_scenes = list(map(lambda name: bpy.data.scenes[name], library_scene_names))
    
    return [level_scene_names, level_scenes, library_scene_names, library_scenes]




def inject_blueprints_list_into_main_scene(scene):
    print("injecting assets/blueprints data into scene")
    root_collection = scene.collection
    assets_list = None
    assets_list_name = f"assets_list_{scene.name}_components"
    for object in scene.objects:
        if object.name == assets_list_name:
            assets_list = object
            break

    if assets_list is None:
        assets_list = make_empty(assets_list_name, [0,0,0], [0,0,0], [0,0,0], root_collection)

    # find all blueprints used in a scene
    # TODO: export a tree rather than a flat list ? because you could have potential clashing items in flat lists (amongst other issues)
    (collection_names, collections) = get_used_collections(scene)
    root_node = CollectionNode()
    root_node.name = "root"
    children_per_collection = {}
    
    #print("collection_names", collection_names, "collections", collections)
    get_sub_collections(collections, root_node, children_per_collection)
    # what about marked assets ?
    # what about audio assets ?
    # what about materials ?
    # object['MaterialInfo'] = '(name: "'+material.name+'", source: "'+current_project_name + '")' 

    #assets_list["blueprints_direct"] = list(collection_names)
    assets_list["BlueprintsList"] = f"({json.dumps(dict(children_per_collection))})"
    #assets_list["Materials"]= '()'

def remove_blueprints_list_from_main_scene(scene):
    assets_list = None
    assets_list_name = f"assets_list_{scene.name}_components"

    for object in scene.objects:
        if object.name == assets_list_name:
            assets_list = object
    if assets_list is not None:
        bpy.data.objects.remove(assets_list, do_unlink=True)
