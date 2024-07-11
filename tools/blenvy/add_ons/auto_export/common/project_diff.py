import json
import bpy
from .serialize_project import serialize_project
from blenvy.settings import load_settings, upsert_settings

def bubble_up_changes(object, changes_per_scene):
    if object is not None and object.parent:
        changes_per_scene[object.parent.name] = bpy.data.objects[object.parent.name]
        bubble_up_changes(object.parent, changes_per_scene)

import uuid
def serialize_current(settings):
    # sigh... you need to save & reset the frame otherwise it saves the values AT THE CURRENT FRAME WHICH CAN DIFFER ACROSS SCENES
    current_frames = [scene.frame_current for scene in bpy.data.scenes]
    for scene in bpy.data.scenes:
        scene.frame_set(0)
        if scene.id_test == '':
            print("GENERATE ID")
            scene.id_test = str(uuid.uuid4())
        print("SCENE ID", scene.id_test)

    current_scene = bpy.context.window.scene
    bpy.context.window.scene = bpy.data.scenes[0]
    #serialize scene at frame 0
    # TODO: add back
    """with bpy.context.temp_override(scene=bpy.data.scenes[1]):
        bpy.context.scene.frame_set(0)"""
    
    current = serialize_project(settings)
    bpy.context.window.scene = current_scene

    # reset previous frames
    for (index, scene) in enumerate(bpy.data.scenes):
        scene.frame_set(int(current_frames[index]))
    
    return current

def get_changes_per_scene(settings):
    previous = load_settings(".blenvy.project_serialized_previous")
    current = serialize_current(settings)

    # determine changes
    changes_per_scene = {}
    changes_per_collection = {}
    changes_per_material = {}
    try:
        (changes_per_scene, changes_per_collection, changes_per_material) = project_diff(previous, current, settings)
    except Exception as error:
        print("failed to compare current serialized scenes to previous ones: Error:", error)

    return changes_per_scene, changes_per_collection, changes_per_material, current


def project_diff(previous, current, settings):
    """print("previous", previous)
    print("current", current)"""
    if previous is None or current is None:
        return {}
    
    changes_per_scene = {}
    changes_per_collection = {}
    changes_per_material = {}

    # TODO : how do we deal with changed scene names ???
    # possible ? on each save, inject an id into each scene, that cannot be copied over
    current_scenes = current["scenes"]
    previous_scenes = previous["scenes"]
    for scene in current_scenes:
        current_object_names =list(current_scenes[scene].keys())

        if scene in previous_scenes: # we can only compare scenes that are in both previous and current data

            previous_object_names = list(previous_scenes[scene].keys())
            added =  list(set(current_object_names) - set(previous_object_names))
            removed = list(set(previous_object_names) - set(current_object_names))
            
            for obj in added:
                if not scene in changes_per_scene:
                    changes_per_scene[scene] = {}
                changes_per_scene[scene][obj] = bpy.data.objects[obj] if obj in bpy.data.objects else None
            
            # TODO: how do we deal with this, as we obviously do not have data for removed objects ?
            for obj in removed:
                if not scene in changes_per_scene:
                    changes_per_scene[scene] = {}
                changes_per_scene[scene][obj] = None

            for object_name in list(current_scenes[scene].keys()): # TODO : exclude directly added/removed objects  
                if object_name in previous_scenes[scene]:
                    current_obj = current_scenes[scene][object_name]
                    prev_obj = previous_scenes[scene][object_name]
                    same = str(current_obj) == str(prev_obj)

                    if not same:
                        if not scene in changes_per_scene:
                            changes_per_scene[scene] = {}

                        target_object = bpy.data.objects[object_name] if object_name in bpy.data.objects else None
                        changes_per_scene[scene][object_name] = target_object
                        bubble_up_changes(target_object, changes_per_scene[scene])
                        # now bubble up for instances & parents
        else:
            print(f"scene {scene} not present in previous data")



    current_collections = current["collections"]
    previous_collections = previous["collections"]

    for collection_name in current_collections:
        if collection_name in previous_collections:
            current_collection = current_collections[collection_name]
            prev_collection = previous_collections[collection_name]
            same = str(current_collection) == str(prev_collection)

            if not same:
                #if not collection_name in changes_per_collection:
                target_collection = bpy.data.collections[collection_name] if collection_name in bpy.data.collections else None
                changes_per_collection[collection_name] = target_collection

    # process changes to materials
    current_materials = current["materials"]
    previous_materials = previous["materials"]

    for material_name in current_materials:
        if material_name in previous_materials:
            current_material = current_materials[material_name]
            prev_material = previous_materials[material_name]
            same = str(current_material) == str(prev_material)

            if not same:
                #if not material_name in changes_per_material:
                target_material = bpy.data.materials[material_name] if material_name in bpy.data.materials else None
                changes_per_material[material_name] = target_material
        
    return (changes_per_scene, changes_per_collection, changes_per_material)