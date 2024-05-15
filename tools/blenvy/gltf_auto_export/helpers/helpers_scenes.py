import json
import bpy
from ...core.object_makers import (make_empty)


# these are mostly for when using this add-on together with the bevy_components add-on
custom_properties_to_filter_out = ['_combine', 'template', 'components_meta']

def is_component_valid_and_enabled(object, component_name):
    if "components_meta" in object or hasattr(object, "components_meta"):
        target_components_metadata = object.components_meta.components
        component_meta = next(filter(lambda component: component["long_name"] == component_name, target_components_metadata), None)
        if component_meta != None:
            return component_meta.enabled and not component_meta.invalid
    return True

def remove_unwanted_custom_properties(object):
    to_remove = []
    component_names = list(object.keys()) # to avoid 'IDPropertyGroup changed size during iteration' issues
    for component_name in component_names:
        if not is_component_valid_and_enabled(object, component_name):
            to_remove.append(component_name)
    for cp in custom_properties_to_filter_out + to_remove:
        if cp in object:
            del object[cp]

# TODO: rename actions ?
# reference https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/addons/io_scene_gltf2/blender/exp/animation/gltf2_blender_gather_action.py#L481
def copy_animation_data(source, target):
    if source.animation_data:
        ad = source.animation_data

        blender_actions = []
        blender_tracks = {}

        # TODO: this might need to be modified/ adapted to match the standard gltf exporter settings
        for track in ad.nla_tracks:
            non_muted_strips = [strip for strip in track.strips if strip.action is not None and strip.mute is False]
            for strip in non_muted_strips: #t.strips:
                # print("  ", source.name,'uses',strip.action.name, "active", strip.active, "action", strip.action)
                blender_actions.append(strip.action)
                blender_tracks[strip.action.name] = track.name

        # Remove duplicate actions.
        blender_actions = list(set(blender_actions))
        # sort animations alphabetically (case insensitive) so they have a defined order and match Blender's Action list
        blender_actions.sort(key = lambda a: a.name.lower())
        
        markers_per_animation = {}
        animations_infos = []

        for action in blender_actions:
            animation_name = blender_tracks[action.name]
            animations_infos.append(
                f'(name: "{animation_name}", frame_start: {action.frame_range[0]}, frame_end: {action.frame_range[1]}, frames_length: {action.frame_range[1] - action.frame_range[0]}, frame_start_override: {action.frame_start}, frame_end_override: {action.frame_end})'
            )
            markers_per_animation[animation_name] = {}

            for marker in action.pose_markers:
                if marker.frame not in markers_per_animation[animation_name]:
                    markers_per_animation[animation_name][marker.frame] = []
                markers_per_animation[animation_name][marker.frame].append(marker.name)

        # best method, using the built-in link animation operator
        with bpy.context.temp_override(active_object=source, selected_editable_objects=[target]): 
            bpy.ops.object.make_links_data(type='ANIMATION')
        
        """if target.animation_data == None:
            target.animation_data_create()
        target.animation_data.action = source.animation_data.action.copy()

        print("copying animation data for", source.name, target.animation_data)
        properties = [p.identifier for p in source.animation_data.bl_rna.properties if not p.is_readonly]
        for prop in properties:
            print("copying stuff", prop)
            setattr(target.animation_data, prop, getattr(source.animation_data, prop))"""
        
        # we add an "AnimationInfos" component 
        target['AnimationInfos'] = f'(animations: {animations_infos})'.replace("'","")
        
        # and animation markers
        markers_formated = '{'
        for animation in markers_per_animation.keys():
            markers_formated += f'"{animation}":'
            markers_formated += "{"
            for frame in markers_per_animation[animation].keys():
                markers = markers_per_animation[animation][frame]
                markers_formated += f"{frame}:{markers}, ".replace("'", '"')
            markers_formated += '}, '             
        markers_formated += '}' 
        target["AnimationMarkers"] = f'( {markers_formated} )'

        
def duplicate_object(object, parent, combine_mode, destination_collection, blueprints_data, nester=""):
    copy = None
    internal_blueprint_names = [blueprint.name for blueprint in blueprints_data.internal_blueprints]
    # print("COMBINE MODE", combine_mode)
    if object.instance_type == 'COLLECTION' and (combine_mode == 'Split' or (combine_mode == 'EmbedExternal' and (object.instance_collection.name in internal_blueprint_names)) ): 
        #print("creating empty for", object.name, object.instance_collection.name, internal_blueprint_names, combine_mode)
        collection_name = object.instance_collection.name
        original_name = object.name

        object.name = original_name + "____bak"
        empty_obj = make_empty(original_name, object.location, object.rotation_euler, object.scale, destination_collection)
        
        """we inject the collection/blueprint name, as a component called 'BlueprintName', but we only do this in the empty, not the original object"""
        empty_obj['BlueprintName'] = '("'+collection_name+'")'
        empty_obj["BlueprintPath"] = ''
        empty_obj['SpawnHere'] = '()'

        # we also inject a list of all sub blueprints, so that the bevy side can preload them
        blueprint_name = collection_name
        children_per_blueprint = {}
        blueprint = blueprints_data.blueprints_per_name.get(blueprint_name, None)
        if blueprint:
            children_per_blueprint[blueprint_name] = blueprint.nested_blueprints
        empty_obj["BlueprintsList"] = f"({json.dumps(dict(children_per_blueprint))})"
        
        # we copy custom properties over from our original object to our empty
        for component_name, component_value in object.items():
            if component_name not in custom_properties_to_filter_out and is_component_valid_and_enabled(object, component_name): #copy only valid properties
                empty_obj[component_name] = component_value
        copy = empty_obj
    else:
        # for objects which are NOT collection instances or when embeding
        # we create a copy of our object and its children, to leave the original one as it is
        original_name = object.name
        object.name = original_name + "____bak"
        copy = object.copy()
        copy.name = original_name

        destination_collection.objects.link(copy)

        """if object.parent == None:
            if parent_empty is not None:
                copy.parent = parent_empty
           """
    # do this both for empty replacements & normal copies
    if parent is not None:
        copy.parent = parent
    remove_unwanted_custom_properties(copy)
    copy_animation_data(object, copy)

    for child in object.children:
        duplicate_object(child, copy, combine_mode, destination_collection, blueprints_data, nester+"  ")

# copies the contents of a collection into another one while replacing library instances with empties
def copy_hollowed_collection_into(source_collection, destination_collection, parent_empty=None, filter=None, blueprints_data=None, addon_prefs={}):
    collection_instances_combine_mode = getattr(addon_prefs, "collection_instances_combine_mode")

    for object in source_collection.objects:
        if object.name.endswith("____bak"): # some objects could already have been handled, ignore them
            continue       
        if filter is not None and filter(object) is False:
            continue
        #check if a specific collection instance does not have an ovveride for combine_mode
        combine_mode = object['_combine'] if '_combine' in object else collection_instances_combine_mode
        parent = parent_empty
        duplicate_object(object, parent, combine_mode, destination_collection, blueprints_data)
        
    # for every child-collection of the source, copy its content into a new sub-collection of the destination
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
            blueprints_data = blueprints_data, 
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
    

    # remove any data we created
    temp_root_collection = temp_scene.collection 
    temp_scene_objects = [o for o in temp_root_collection.all_objects]
    for object in temp_scene_objects:
        #print("removing", object.name)
        bpy.data.objects.remove(object, do_unlink=True)

    # remove the temporary scene
    bpy.data.scenes.remove(temp_scene, do_unlink=True)
    
    # reset original names
    restore_original_names(original_root_collection)

# convenience utility to get lists of scenes
def get_scenes(addon_prefs):
    level_scene_names= getattr(addon_prefs,"main_scene_names", []) #list(map(lambda scene: scene.name, getattr(addon_prefs,"main_scenes")))
    library_scene_names = getattr(addon_prefs,"library_scene_names", []) #list(map(lambda scene: scene.name, getattr(addon_prefs,"library_scenes")))

    level_scene_names = list(filter(lambda name: name in bpy.data.scenes, level_scene_names))
    library_scene_names = list(filter(lambda name: name in bpy.data.scenes, library_scene_names))

    level_scenes = list(map(lambda name: bpy.data.scenes[name], level_scene_names))
    library_scenes = list(map(lambda name: bpy.data.scenes[name], library_scene_names))
    
    return [level_scene_names, level_scenes, library_scene_names, library_scenes]
