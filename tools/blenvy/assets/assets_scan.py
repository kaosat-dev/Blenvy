import os
import json
import bpy

from .asset_helpers import does_asset_exist, get_user_assets, get_user_assets_as_list

def scan_assets(scene, blueprints_data, addon_prefs):
    export_root_path = getattr(addon_prefs, "export_root_path")
    export_output_folder = getattr(addon_prefs,"export_output_folder")
    export_levels_path = getattr(addon_prefs,"export_levels_path")
    export_blueprints_path = getattr(addon_prefs, "export_blueprints_path")
    export_gltf_extension = getattr(addon_prefs, "export_gltf_extension")

    relative_blueprints_path = os.path.relpath(export_blueprints_path, export_root_path)
    blueprint_instance_names_for_scene = blueprints_data.blueprint_instances_per_main_scene.get(scene.name, None)

    blueprint_assets_list = []
    if blueprint_instance_names_for_scene:
        for blueprint_name in blueprint_instance_names_for_scene:
            blueprint = blueprints_data.blueprints_per_name.get(blueprint_name, None)
            if blueprint is not None: 
                print("BLUEPRINT", blueprint)
                blueprint_exported_path = None
                if blueprint.local:
                    blueprint_exported_path = os.path.join(relative_blueprints_path, f"{blueprint.name}{export_gltf_extension}")
                else:
                    # get the injected path of the external blueprints
                    blueprint_exported_path = blueprint.collection['Export_path'] if 'Export_path' in blueprint.collection else None
                    print("foo", dict(blueprint.collection))
                if blueprint_exported_path is not None:
                    blueprint_assets_list.append({"name": blueprint.name, "path": blueprint_exported_path})
                

    # fetch images/textures
    # see https://blender.stackexchange.com/questions/139859/how-to-get-absolute-file-path-for-linked-texture-image
    textures = []
    for ob in bpy.data.objects:
        if ob.type == "MESH":
            for mat_slot in ob.material_slots:
                if mat_slot.material:
                    if mat_slot.material.node_tree:
                        textures.extend([x.image.filepath for x in mat_slot.material.node_tree.nodes if x.type=='TEX_IMAGE'])
    print("textures", textures)

    assets_list_name = f"assets_{scene.name}"
    assets_list_data = {"blueprints": json.dumps(blueprint_assets_list), "sounds":[], "images":[]}

    print("blueprint assets", blueprint_assets_list)


def get_userTextures():
    # TODO: limit this to the ones actually in use
    # fetch images/textures
    # see https://blender.stackexchange.com/questions/139859/how-to-get-absolute-file-path-for-linked-texture-image
    textures = []
    for ob in bpy.data.objects:
        if ob.type == "MESH":
            for mat_slot in ob.material_slots:
                if mat_slot.material:
                    if mat_slot.material.node_tree:
                        textures.extend([x.image.filepath for x in mat_slot.material.node_tree.nodes if x.type=='TEX_IMAGE'])
    print("textures", textures)

def get_blueprint_assets_tree(blueprint, blueprints_data, parent, addon_prefs):
    export_blueprints_path = getattr(addon_prefs, "export_blueprints_path")
    export_gltf_extension = getattr(addon_prefs, "export_gltf_extension")
    assets_list = []
    

    for blueprint_name in blueprint.nested_blueprints:
        child_blueprint = blueprints_data.blueprints_per_name.get(blueprint_name, None)
        if child_blueprint:
            blueprint_exported_path = None
            if blueprint.local:
                blueprint_exported_path = os.path.join(export_blueprints_path, f"{child_blueprint.name}{export_gltf_extension}")
            else:
                # get the injected path of the external blueprints
                blueprint_exported_path = child_blueprint.collection['export_path'] if 'export_path' in child_blueprint.collection else None
            if blueprint_exported_path is not None:
                assets_list.append({"name": child_blueprint.name, "path": blueprint_exported_path, "type": "MODEL", "generated": True,"internal":blueprint.local, "parent": blueprint.name})

            # and add sub stuff
            sub_assets_lists = get_blueprint_assets_tree(child_blueprint, blueprints_data, parent=child_blueprint.name, addon_prefs=addon_prefs)
            assets_list += sub_assets_lists

    direct_assets = get_user_assets_as_list(blueprint.collection)
    for asset in direct_assets:
        asset["parent"] = parent
        asset["internal"] = blueprint.local
    assets_list += direct_assets
    return assets_list

def get_main_scene_assets_tree(main_scene, blueprints_data, addon_prefs):
    export_blueprints_path =  getattr(addon_prefs, "export_blueprints_path")
    export_gltf_extension = getattr(addon_prefs, "export_gltf_extension")
    blueprint_instance_names_for_scene = blueprints_data.blueprint_instances_per_main_scene.get(main_scene.name, None)

    assets_list = get_user_assets_as_list(main_scene)
    if blueprint_instance_names_for_scene:
        for blueprint_name in blueprint_instance_names_for_scene:
            blueprint = blueprints_data.blueprints_per_name.get(blueprint_name, None)
            if blueprint is not None: 
                blueprint_exported_path = None
                if blueprint.local:
                    blueprint_exported_path = os.path.join(export_blueprints_path, f"{blueprint.name}{export_gltf_extension}")
                else:
                    # get the injected path of the external blueprints
                    blueprint_exported_path = blueprint.collection['export_path'] if 'export_path' in blueprint.collection else None
                if blueprint_exported_path is not None and not does_asset_exist(assets_list, blueprint_exported_path):
                    assets_list.append({"name": blueprint.name, "path": blueprint_exported_path, "type": "MODEL", "generated": True, "internal":blueprint.local, "parent": None})
                
                assets_list += get_blueprint_assets_tree(blueprint, blueprints_data, parent=blueprint.name, addon_prefs=addon_prefs)

    print("TOTAL ASSETS", assets_list)
    return assets_list
