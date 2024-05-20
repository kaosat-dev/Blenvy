import json
from mathutils import Color
import numpy as np
import bpy
from ..constants import TEMPSCENE_PREFIX

fields_to_ignore_generic = ["tag", "type", "update_tag", "use_extra_user", "use_fake_user", "user_clear", "user_of_id", "user_remap", "users",
                    'animation_data_clear', 'animation_data_create', 'asset_clear', 'asset_data', 'asset_generate_preview', 'asset_mark', 'bl_rna', 'evaluated_get',
                    'library', 'library_weak_reference', 'make_local','name', 'name_full', 'original',
                        'override_create', 'override_hierarchy_create', 'override_library', 'preview', 'preview_ensure', 'rna_type',
                        'session_uid', 'copy', 'id_type', 'is_embedded_data', 'is_evaluated', 'is_library_indirect', 'is_missing', 'is_runtime_data']

# possible alternatives https://blender.stackexchange.com/questions/286010/bpy-detect-modified-mesh-data-vertices-edges-loops-or-polygons-for-cachin
def mesh_hash(obj):
    # this is incomplete, how about edges ?
    vertex_count = len(obj.data.vertices)
    vertices_np = np.empty(vertex_count * 3, dtype=np.float32)
    obj.data.vertices.foreach_get("co", vertices_np)
    h = str(hash(vertices_np.tobytes()))
    return h

# TODO: redo this one, this is essentially modifiec copy & pasted data, not fitting
def animation_hash(obj):
    animation_data = obj.animation_data
    if not animation_data:
        return None
    blender_actions = []
    blender_tracks = {}

    # TODO: this might need to be modified/ adapted to match the standard gltf exporter settings
    for track in animation_data.nla_tracks:
        strips = [strip for strip in track.strips if strip.action is not None]
        for strip in strips: 
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

    compact_result = hash(str((blender_actions, blender_tracks, markers_per_animation, animations_infos)))
    return compact_result


def camera_hash(obj):
    camera_fields = ["angle", "angle_x", "angle_y", "animation_data", "background_images", "clip_end", "clip_start", "display_size", "dof", "fisheye_fov"]
    camera_data = obj.data
    fields_to_ignore= fields_to_ignore_generic

    all_field_names = dir(camera_data)
    fields = [getattr(camera_data, prop, None) for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]
    # TODO: the above is not enough, certain fields are left as bpy.data.xx
    #print("camera", obj, fields)
    return str(fields)

def light_hash(obj):
    light_data = obj.data
    fields_to_ignore = fields_to_ignore_generic

    all_field_names = dir(light_data)
    fields = [getattr(light_data, prop, None) for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]
    return str(fields)

def bones_hash(bones):
    fields_to_ignore = fields_to_ignore_generic + ['AxisRollFromMatrix', 'MatrixFromAxisRoll', 'evaluate_envelope', 'convert_local_to_pose', 'foreach_get', 'foreach_set', 'get', 'set', 'find', 'items', 'keys', 'values']
    
    bones_result = []
    for bone in bones: 
        all_field_names = dir(bone)
        fields = [getattr(bone, prop, None)  for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]
        bones_result.append(fields)
    #print("fields of bone", bones_result)
    return str(hash(str(bones_result)))

# fixme: not good enough ?
def armature_hash(obj):
    fields_to_ignore = fields_to_ignore_generic + ['display_type', 'is_editmode', 'pose_position', 'foreach_get', 'get']
    fields_to_convert = {'bones': bones_hash}#, 'collections_all': bones_hash}
    armature_data = obj.data
    all_field_names = dir(armature_data)

    fields = [getattr(armature_data, prop, None) if not prop in fields_to_convert.keys() else fields_to_convert[prop](getattr(armature_data, prop)) for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]
    #print("ARMATURE", fields)

    """for bone in armature_data.bones:
        print("bone", bone, bone_hash(bone))"""
    return str(fields)

def field_value(data):
    pass

def color(color_data):
    # print("color", color_data, type(color_data))
    return str(peel_value(color_data))

def lineart(lineart_data):
    fields_to_ignore = fields_to_ignore_generic

    all_field_names = dir(lineart_data)
    fields = [getattr(lineart_data, prop, None) for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]
    return str(fields)

def node_tree(nodetree_data):
    fields_to_ignore = fields_to_ignore_generic+ ['contains_tree','get_output_node', 'interface_update', 'override_template_create']
    all_field_names = dir(nodetree_data)
    fields = [getattr(nodetree_data, prop, None) for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]

    # print("node tree", fields)
    return str(fields)


def peel_value( value ):
        try:
            len( value )
            return [ peel_value( x ) for x in value ]
        except TypeError:
            return value

def material_hash(material):
    fields_to_ignore = fields_to_ignore_generic
    fields_to_convert = {'diffuse_color': color, 'line_color': color, 'lineart': lineart, 'node_tree': node_tree} # TODO: perhaps use types rather than names
    all_field_names = dir(material)
    fields = [getattr(material, prop, None) if not prop in fields_to_convert.keys() else fields_to_convert[prop](getattr(material, prop)) for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]

    type_of = [type(getattr(material, prop, None))  for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]
    names = [prop for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]

    tutu = [t == Color for t in type_of] # bpy.types.MaterialLineArt bpy.types.ShaderNodeTree
    #print("fields", type_of)

    """for prop in [prop for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]:
        bla = getattr(material, prop, None)
        if hasattr(bla, "rna_type"):
            print("YOLO", prop, bla, peel_value(bla), "type", type(bla), bla.rna_type, bla.rna_type == bpy.types.FloatProperty, type(bla) == bpy.types.bpy_prop_collection)
            print("types", type(bla) == bpy.types.bpy_prop_collection, type(bla) == bpy.types.FloatColorAttributeValue)"""
            
    # print("oooooh", material, material.bl_rna.properties.items())

    return str(fields)#str(hash(str(fields)))

# TODO: this is partially taken from export_materials utilities, perhaps we could avoid having to fetch things multiple times ?
def materials_hash(obj, cache):
    # print("materials")
    materials = []
    for material_slot in obj.material_slots:
        material = material_slot.material
        cached_hash = cache['materials'].get(material.name, None)
        if cached_hash:
            # print("CACHHHHHED", cached_hash)
            materials.append(cached_hash)
        else:
            mat = material_hash(material)
            cache['materials'][material.name] = mat
            materials.append(mat)
            # print("NOT CACHHH", mat)

    # materials = [material_hash(material_slot.material) if not material_slot.material.name in cache["materials"] else cache["materials"][material_slot.material.name]  for material_slot in obj.material_slots]
    return str(hash(str(materials)))

def custom_properties_hash(obj):
    custom_properties = {}
    for property_name in obj.keys():
        if property_name not in '_RNA_UI' and property_name != 'components_meta':
            custom_properties[property_name] = obj[property_name]

    return str(hash(str(custom_properties)))
    

def serialize_scene(): 
    cache = {"materials":{}}
    print("serializing scene")
    data = {}
    for scene in bpy.data.scenes:
        if scene.name.startswith(TEMPSCENE_PREFIX):
            continue
        data[scene.name] = {}
        for object in scene.objects:
            object = bpy.data.objects[object.name]

            #loc, rot, scale = bpy.context.object.matrix_world.decompose()

            transform = str((object.location, object.rotation_euler, object.scale)) #str((object.matrix_world.to_translation(), object.matrix_world.to_euler('XYZ'), object.matrix_world.to_quaternion()))#
            visibility = object.visible_get()            
            custom_properties = custom_properties_hash(object) if len(object.keys()) > 0 else None
            animations = animation_hash(object)
            mesh = mesh_hash(object) if object.type == 'MESH' else None
            camera = camera_hash(object) if object.type == 'CAMERA' else None
            light = light_hash(object) if object.type == 'LIGHT' else None
            armature = armature_hash(object) if object.type == 'ARMATURE' else None
            parent = object.parent.name if object.parent else None
            collections = [collection.name for collection in object.users_collection]
            materials = materials_hash(object, cache) if len(object.material_slots) > 0 else None

            data[scene.name][object.name] = {
                "name": object.name,
                "transforms": transform,
                "visibility": visibility,
                "custom_properties": custom_properties,
                "animations": animations,
                "mesh": mesh,
                "camera": camera,
                "light": light,
                "armature": armature,
                "parent": parent,
                "collections": collections,
                "materials": materials
            }

    """print("data", data)
    print("")
    print("")
    print("data json", json.dumps(data))"""

    return data # json.dumps(data)


