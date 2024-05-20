import json
import bpy
from ..helpers.serialize_scene import serialize_scene

def bubble_up_changes(object, changes_per_scene):
    if object.parent:
        changes_per_scene[object.parent.name] = bpy.data.objects[object.parent.name]
        bubble_up_changes(object.parent, changes_per_scene)


def foo():
    current = json.loads(current)

    previous_stored = bpy.data.texts[".TESTING"] if ".TESTING" in bpy.data.texts else None # bpy.data.texts.new(".TESTING")
    if previous_stored == None:
        previous_stored = bpy.data.texts.new(".TESTING")
        previous_stored.write(current)
        return {}
    previous = json.loads(previous_stored.as_string())


    previous_stored.clear()
    previous_stored.write(json.dumps(current))

    
def serialize_current():
    # sigh... you need to save & reset the frame otherwise it saves the values AT THE CURRENT FRAME WHICH CAN DIFFER ACROSS SCENES
    current_frames = [scene.frame_current for scene in bpy.data.scenes]
    for scene in bpy.data.scenes:
        scene.frame_set(0)

    current_scene = bpy.context.window.scene
    bpy.context.window.scene = bpy.data.scenes[0]
    #serialize scene at frame 0
    """with bpy.context.temp_override(scene=bpy.data.scenes[1]):
        bpy.context.scene.frame_set(0)"""
    current = serialize_scene()
    bpy.context.window.scene = current_scene

    # reset previous frames
    for (index, scene) in enumerate(bpy.data.scenes):
        scene.frame_set(int(current_frames[index]))
    
    return current

def get_changes_per_scene():
    current = serialize_current()

    previous_stored = bpy.data.texts[".blenvy.project.serialized"] if ".blenvy.project.serialized" in bpy.data.texts else None
    if previous_stored == None:
        previous_stored = bpy.data.texts.new(".blenvy.project.serialized")
        previous_stored.write(json.dumps(current))
        return {}
    
    previous = json.loads(previous_stored.as_string())
    
    # determin changes
    changes_per_scene = project_diff(previous, current)

    # save the current project as previous
    previous_stored.clear()
    previous_stored.write(json.dumps(current))
    return changes_per_scene


def project_diff(previous, current):
    
    changes_per_scene = {}

    # TODO : how do we deal with changed scene names ???
    for scene in current:
        print("SCENE", scene)
        previous_object_names = list(previous[scene].keys())
        current_object_names =list(current[scene].keys())
        added =  list(set(current_object_names) - set(previous_object_names))
        removed = list(set(previous_object_names) - set(current_object_names))
        
        for obj in added:
            if not scene in changes_per_scene:
                changes_per_scene[scene] = {}
            changes_per_scene[scene][obj] = bpy.data.objects[obj]
        
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

                    changes_per_scene[scene][object_name] = bpy.data.objects[object_name]
                    bubble_up_changes(bpy.data.objects[object_name], changes_per_scene[scene])
                    # now bubble up for instances & parents
        
    print("changes per scene", changes_per_scene)
    return changes_per_scene