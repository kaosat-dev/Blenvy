

import bpy
import os


# TODO: move to helpers

def find_animations_not_on_disk(animations, animations_path_full, extension):
    not_found_animations = []
    for animation in animations:
        gltf_output_path = os.path.join(animations_path_full, animation["armature"].name + extension)
        # print("gltf_output_path", gltf_output_path)
        found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
        if not found:
            not_found_animations.append(animation)
    return not_found_animations

def add_animation_info_to_objects(animations_per, settings):
    materials_path =  getattr(settings, "materials_path")
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")
    for object in materials_per_object.keys():
        material_infos = []
        for material in materials_per_object[object]:
            materials_exported_path = posixpath.join(materials_path, f"{material.name}{export_gltf_extension}")
            material_info = f'(name: "{material.name}", path: "{materials_exported_path}")' 
            material_infos.append(material_info)
        # problem with using actual components: you NEED the type registry/component infos, so if there is none , or it is not loaded yet, it does not work
        # for a few components we could hardcode this
        component_value = f"({material_infos})".replace("'","")
        '''try:
            bpy.ops.blenvy.component_add(target_item_name=object.name, target_item_type="OBJECT", component_type="blenvy::blueprints::materials::MaterialInfos", component_value=component_value )
        except:'''
        object['MaterialInfos'] = f"({material_infos})".replace("'","") 
            #upsert_bevy_component(object, "blenvy::blueprints::materials::MaterialInfos", f"({material_infos})".replace("'","") )
            #apply_propertyGroup_values_to_item_customProperties_for_component(object, "MaterialInfos")
        print("adding materialInfos to object", object, "material infos", material_infos)


def get_animations_to_export(changed_animations, changed_export_parameters, blueprints_data, settings):
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")
    animations_path_full = getattr(settings,"animations_path_full", "")
    split_out_animations = getattr(settings.auto_export, "split_out_animations")

    change_detection = getattr(settings.auto_export, "change_detection")

    all_animations = []
    animations_to_export = []
    objects_per_armature = {}
    armature_objects = {} # often we need the object of the armature, not the armature itself

    
    # TODO: how to deal with non armatures ?
    for object in bpy.data.objects:
        if len(object.modifiers) > 0:
            for modifier in object.modifiers:
                if modifier.type == 'ARMATURE':
                    ref = modifier.object.name
                    armature_name = bpy.data.objects[ref].data.name
                    armature = bpy.data.armatures[armature_name]
                    if not armature.name in objects_per_armature :
                        objects_per_armature[armature.name] = []
                    objects_per_armature[armature.name].append(object)
                    armature_objects[armature.name] = modifier.object
                    print("Object has armature", object, modifier, modifier.object, "armature", armature.name)

        
        """animation_data = object.animation_data
        if animation_data is not None:
            print("ANIMATION DATA", animation_data, "for object", object)
            if len(object.modifiers) > 0:
                for modifier in object.modifiers:
                    if modifier.type == 'ARMATURE':
                        print("YOHOHOHO", modifier, modifier.object)

                        ref = modifier.object.name
                        armature_name = bpy.data.objects[ref].data.name
                        armature = bpy.data.armatures[armature_name]
                        if not armature.name in objects_per_armature :
                            objects_per_armature[armature.name] = []
                        objects_per_armature[armature.name].append(object)"""


            #animations_to_export.append(object)
    for armature_name in objects_per_armature.keys():
        all_animations.append({"armature": bpy.data.armatures[armature_name], "armature_object": armature_objects[armature_name],  "objects": objects_per_armature[armature_name]})
  

    local_animations = [animation for animation in all_animations if animation["armature_object"].library is None]
    animations_to_export = []

    if split_out_animations and change_detection:
        if changed_export_parameters:
            animations_to_export = local_animations
        else :
            # first check if all animations have already been exported before (if this is the first time the exporter is run
            # in your current Blender session for example)
            animations_not_on_disk = find_animations_not_on_disk(local_animations, animations_path_full, export_gltf_extension)
            animations_always_export = []
            animations_to_export =  list(set(changed_animations + animations_not_on_disk + animations_always_export))

    print("animations_to_export", animations_to_export)
    return animations_to_export