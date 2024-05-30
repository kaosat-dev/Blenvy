import inspect
import json
from mathutils import Color
import numpy as np
import bpy
from ..constants import TEMPSCENE_PREFIX


fields_to_ignore_generic = [
    "tag", "type", "update_tag", "use_extra_user", "use_fake_user", "user_clear", "user_of_id", "user_remap", "users",
    'animation_data_clear', 'animation_data_create', 'asset_clear', 'asset_data', 'asset_generate_preview', 'asset_mark', 'bl_rna', 'evaluated_get',
    'library', 'library_weak_reference', 'make_local','name', 'name_full', 'original',
    'override_create', 'override_hierarchy_create', 'override_library', 'preview', 'preview_ensure', 'rna_type',
    'session_uid', 'copy', 'id_type', 'is_embedded_data', 'is_evaluated', 'is_library_indirect', 'is_missing', 'is_runtime_data'
]


def generic_fields_hasher(data, fields_to_ignore):
    all_field_names = dir(data)
    field_values = [getattr(data, prop, None) for prop in all_field_names  if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show") and not callable(getattr(data, prop, None))  ]
    return str(field_values)

def peel_value( value ):
        try:
            len( value )
            return [ peel_value( x ) for x in value ]
        except TypeError:
            return value

def _lookup_color(data):
    return peel_value(data)

def _lookup_array(data):
    return peel_value(data)

def _lookup_prop_group(data):
    bla = generic_fields_hasher_evolved(data, fields_to_ignore=fields_to_ignore_generic)
    print("PROPGROUP", bla)
    return bla

def _lookup_collection(data):
    return [generic_fields_hasher_evolved(item, fields_to_ignore=fields_to_ignore_generic) for item in data]

def _lookup_materialLineArt(data):
    return generic_fields_hasher_evolved(data, fields_to_ignore=fields_to_ignore_generic)

type_lookups = {
    Color: _lookup_color,#lambda input: print("dsf")',
    bpy.types.bpy_prop_array: _lookup_array,
    bpy.types.PropertyGroup: _lookup_prop_group,
    bpy.types.bpy_prop_collection: _lookup_collection,
    bpy.types.MaterialLineArt: _lookup_materialLineArt
}

# TODO: replace the first one with this once if its done 
def generic_fields_hasher_evolved(data, fields_to_ignore):
    all_field_names = dir(data)
    field_values = []
    for field_name in all_field_names:
        if not field_name.startswith("__") and not field_name in fields_to_ignore and not field_name.startswith("show") and not callable(getattr(data, field_name, None)):
            raw_value = getattr(data, field_name, None)
            #print("raw value", raw_value, "type", type(raw_value), isinstance(raw_value, Color), isinstance(raw_value, bpy.types.bpy_prop_array))
            conversion_lookup = None # type_lookups.get(type(raw_value), None)
            all_types = inspect.getmro(type(raw_value))            
            for s_type in all_types:
                if type_lookups.get(s_type, None) is not None:
                    conversion_lookup = type_lookups[s_type]
                    break

            field_value = None
            if conversion_lookup is not None:
                field_value =  conversion_lookup(raw_value)
                print("field_name",field_name,"conv value", field_value)
            else:
                print("field_name",field_name,"raw value", raw_value)
                field_value = raw_value
            
            field_values.append(str(field_value))

    return str(field_values)

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


# TODO : we should also check for custom props on scenes, meshes, materials
# TODO: also how about our new "assets" custom properties ? those need to be check too
def custom_properties_hash(obj):
    custom_properties = {}
    for property_name in obj.keys():
        if property_name not in '_RNA_UI' and property_name != 'components_meta':
            custom_properties[property_name] = obj[property_name]
    return str(hash(str(custom_properties)))

def camera_hash(obj):
    camera_data = obj.data
    # TODO: the above is not enough, certain fields are left as bpy.data.xx
    return str(generic_fields_hasher(camera_data, fields_to_ignore_generic))

def light_hash(obj):
    light_data = obj.data
    return str(generic_fields_hasher(light_data, fields_to_ignore_generic))

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

    """for bone in armature_data.bones:
        print("bone", bone, bone_hash(bone))"""
    return str(fields)


def node_tree(nodetree_data):
    print("SCANNING NODE TREE", nodetree_data)
    # output node:
    output = nodetree_data.get_output_node("ALL")
    print("output", output)

    fields_to_ignore = fields_to_ignore_generic+ ['contains_tree','get_output_node', 'interface_update', 'override_template_create']
    all_field_names = dir(nodetree_data)
    fields = [getattr(nodetree_data, prop, None) for prop in all_field_names if not prop.startswith("__") and not prop in fields_to_ignore and not prop.startswith("show_")]

    # print("node tree", fields)
    return str(fields)

def material_hash(material, settings):
    print("material_hash", material)
    hashed_material = generic_fields_hasher_evolved(material, fields_to_ignore_generic + ['node_tree']) # we want to handle the node tree seperatly
    print("HASH", hashed_material)
    """if node_group is not None and settings.auto_export.materials_in_depth_scan:
        pass
    else:
        generic_fields_hasher(material, fields_to_ignore_generic)"""
    return str(hashed_material)

# TODO: this is partially taken from export_materials utilities, perhaps we could avoid having to fetch things multiple times ?
def materials_hash(obj, cache, settings):
    # print("materials")
    materials = []
    for material_slot in obj.material_slots:
        material = material_slot.material
        """cached_hash = cache['materials'].get(material.name, None)
        if cached_hash:
            materials.append(cached_hash)
            print("CAACHED")
        else:
            mat = material_hash(material, settings)
            cache['materials'][material.name] = mat
            materials.append(mat)"""
        mat = material_hash(material, settings)
        cache['materials'][material.name] = mat
        materials.append(mat)

    return str(hash(str(materials)))

def modifier_hash(modifier_data, settings):
    node_group = getattr(modifier_data, "node_group", None)

    if node_group is not None and settings.auto_export.modifiers_in_depth_scan:
        #print("THIS IS A GEOMETRY NODE") 

        # storage for hashing
        links_hashes = []
        nodes_hashes = []
        modifier_inputs = dict(modifier_data)

        for node in node_group.nodes:
            #print("node", node, node.type, node.name, node.label)
            #print("node info", dir(node))

            input_hashes = []
            for input in node.inputs:
                #print(" input", input, "label", input.label, "name", input.name)
                input_hash = f"{getattr(input, 'default_value', None)}"
                input_hashes.append(input_hash)
                """if hasattr(input, "default_value"):
                    print("YOHO", dict(input), input.default_value)"""

            output_hashes = []
            # IF the node itself is a group input, its outputs are the inputs of the geometry node (yes, not easy)
            node_in_use = True
            for (index, output) in enumerate(node.outputs):
                # print(" output", output, "label", output.label, "name", output.name, "generated name", f"Socket_{index+1}")
                output_hash = f"{getattr(output, 'default_value', None)}"
                output_hashes.append(output_hash)
                """if hasattr(output, "default_value"):
                    print("YOHO", output.default_value)"""
                node_in_use = node_in_use and hasattr(output, "default_value")
            #print("NODE IN USE", node_in_use)

            node_fields_to_ignore = fields_to_ignore_generic + ['internal_links', 'inputs', 'outputs']

            node_hash = f"{generic_fields_hasher(node, node_fields_to_ignore)}_{str(input_hashes)}_{str(output_hashes)}"
            #print("node hash", node_hash)
            nodes_hashes.append(node_hash)
            #print(" ")

        for link in node_group.links:
            """print("LINK", link) #dir(link)
            print("FROM", link.from_node, link.from_socket)
            print("TO", link.to_node, link.to_socket)"""


            from_socket_default = link.from_socket.default_value if hasattr(link.from_socket, "default_value") else None
            to_socket_default = link.to_socket.default_value if hasattr(link.to_socket, "default_value") else None

            link_hash = f"{link.from_node.name}_{link.from_socket.name}_{from_socket_default}+{link.to_node.name}_{link.to_socket.name}_{to_socket_default}"

            """if hasattr(link.from_socket, "default_value"):
                print("[FROM SOCKET]", link.from_socket.default_value)
            if hasattr(link.to_socket, "default_value"):
                print("[TO SOCKET]", link.to_socket.default_value)"""

            links_hashes.append(link_hash)
            #print("link_hash", link_hash)

        return f"{str(modifier_inputs)}_{str(nodes_hashes)}_{str(links_hashes)}"
    else:
        return generic_fields_hasher(modifier_data, fields_to_ignore_generic)
    

def modifiers_hash(object, settings):
    modifiers = []
    for modifier in object.modifiers:
        print("modifier", modifier )# modifier.node_group)
        modifiers.append(modifier_hash(modifier, settings))
        print("  ")
    return str(hash(str(modifiers)))

def serialize_scene(settings): 
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
            materials = materials_hash(object, cache, settings) if len(object.material_slots) > 0 else None
            modifiers = modifiers_hash(object, settings) if len(object.modifiers) > 0 else None


            object_field_hashes = {
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
                "materials": materials,
                "modifiers":modifiers
            }
            object_field_hashes_filtered = {key: object_field_hashes[key] for key in object_field_hashes.keys() if object_field_hashes[key] is not None}
            objectHash = str(hash(str(object_field_hashes_filtered)))
            data[scene.name][object.name] = objectHash

    """print("data", data)
    print("")
    print("")
    print("data json", json.dumps(data))"""

    return data # json.dumps(data)


