import os
import bpy

from ....core.helpers_collections import traverse_tree
from ..common.duplicate_object import copy_animation_data
from ..common.generate_temporary_scene_and_export import generate_temporary_scene_and_export
from ..common.export_gltf import (generate_gltf_export_settings)

def duplicate_object(object, destination_collection):
    copy = None    
    # for objects which are NOT collection instances or when embeding
    # we create a copy of our object and its children, to leave the original one as it is
    original_name = object.name
    #object.name = original_name + "____bak"
    copy = object.copy()
    copy.name = original_name


    destination_collection.objects.link(copy)
    copy_animation_data(object, copy)

    animation_data = copy.animation_data
    print("COPY ANIMATION DATA", animation_data)

    # we want to hide our objects so we only export their bones if any
    #copy.hide_set(True)


# clear & remove "hollow scene"
def clear_animation_scene_alt(temp_scene):   
    # remove any data we created
    temp_root_collection = temp_scene.collection 
    temp_scene_objects = [o for o in temp_root_collection.all_objects]
    for object in temp_scene_objects:
        #print("removing", object.name)
        bpy.data.objects.remove(object, do_unlink=True)

    # remove the temporary scene
    bpy.data.scenes.remove(temp_scene, do_unlink=True)
    
    # reset original names
    for object in temp_root_collection.all_objects:
        if object.name.endswith("____bak"):
            object.name = object.name.replace("____bak", "")

# generates a scene for a given animated object
def generate_animation_scene_content(root_collection, animation):
    """for object in animation["objects"]:
        duplicate_object(object, root_collection)"""
    armature_object = animation["armature_object"] # we want the object , not the armature itself (the object is a container, and we can only copy objects to our temporary scene, not armatures)
    print("generate scene for", armature_object)
    duplicate_object(armature_object, root_collection)
    #raise Exception("arg")
    return {}

def clear_animation_scene(temp_scene):
    print("CLEAR ANIMATION SCENE")
    root_collection = temp_scene.collection 
    scene_objects = [o for o in root_collection.objects]
    for object in scene_objects:       
        try:
            bpy.data.objects.remove(object, do_unlink=True)
        except:pass

    bpy.data.scenes.remove(temp_scene)


# exports the animations used inside the current project:
# see https://forum.babylonjs.com/t/blender-how-to-export-animations-only-like-elf-glft/45716/2
# PROBLEM: it grabs the wrong objects ! 
# we need to hide the meshes that have armatures and keep the armature itself
def export_animations(animations_to_export, settings, blueprints_data):
    gltf_export_settings = generate_gltf_export_settings(settings)
    animations_path_full = getattr(settings,"animations_path_full", "")

    gltf_export_settings = { **gltf_export_settings, 
                    'use_active_scene': True, 
                    'use_active_collection':True, 
                    'use_active_collection_with_nested':True,  
                    'use_visible': True,
                    'use_renderable': False,
                    'export_apply':True,
                    'export_animations': True # since we want to export animations , forced to true
                    }
    for animation in animations_to_export:
        print("exporting animation from ", animation)
        gltf_output_path = os.path.join(animations_path_full, animation["armature"].name)

        generate_temporary_scene_and_export(
            settings=settings, 
            gltf_export_settings=gltf_export_settings,
            temp_scene_name="__animation_scene"+ animation["armature"].name,
            gltf_output_path=gltf_output_path,
            tempScene_filler= lambda temp_collection: generate_animation_scene_content(temp_collection, animation),
            tempScene_cleaner= lambda temp_scene, params: clear_animation_scene(temp_scene=temp_scene)
        )
