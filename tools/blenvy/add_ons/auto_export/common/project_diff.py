import json
import bpy
from .serialize_scene import serialize_scene
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
    """with bpy.context.temp_override(scene=bpy.data.scenes[1]):
        bpy.context.scene.frame_set(0)"""
    
    current = serialize_scene(settings)
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
    try:
        changes_per_scene = project_diff(previous, current, settings)
    except Exception as error:
        print("failed to compare current serialized scenes to previous ones", error)

    # save the current project as previous
    upsert_settings(".blenvy.project_serialized_previous", current, overwrite=True)

    print("changes per scene", changes_per_scene)
    return changes_per_scene


def project_diff(previous, current, settings):
    """print("previous", previous)
    print("current", current)"""
    if previous is None or current is None:
        return {}
    print("Settings", settings,"current", current, "previous", previous)
    
    changes_per_scene = {}

    # TODO : how do we deal with changed scene names ???
    # possible ? on each save, inject an id into each scene, that cannot be copied over

    print('TEST SCENE', bpy.data.scenes.get("ULTRA LEVEL2"), None)

    for scene in current:
        print("SCENE", scene)
        current_object_names =list(current[scene].keys())

        if scene in previous: # we can only compare scenes that are in both previous and current data

            previous_object_names = list(previous[scene].keys())
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

            for object_name in list(current[scene].keys()): # TODO : exclude directly added/removed objects  
                if object_name in previous[scene]:
                    current_obj = current[scene][object_name]
                    prev_obj = previous[scene][object_name]
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
        
    return changes_per_scene