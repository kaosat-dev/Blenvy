import bpy
import json
import os
import uuid
from pathlib import Path
from bpy_types import (PropertyGroup)
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty, CollectionProperty)


def get_assets(scene, blueprints_data, addon_prefs):
    export_root_folder = getattr(addon_prefs, "export_root_folder")
    export_output_folder = getattr(addon_prefs,"export_output_folder")
    export_levels_path = getattr(addon_prefs,"export_levels_path")
    export_blueprints_path = getattr(addon_prefs, "export_blueprints_path")
    export_gltf_extension = getattr(addon_prefs, "export_gltf_extension")

    relative_blueprints_path = os.path.relpath(export_blueprints_path, export_root_folder)
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


# this is where we store the information for all available assets
#
class AssetsRegistry(PropertyGroup):
    assets_list = []

    asset_name_selector: StringProperty(
        name="asset name",
        description="name of asset to add",
    ) # type: ignore

    asset_type_selector: EnumProperty(
        name="asset type",
        description="type of asset to add",
         items=(
                ('MODEL', "Model", ""),
                ('AUDIO', "Audio", ""),
                ('IMAGE', "Image", ""),
                )
    ) # type: ignore

    asset_path_selector: StringProperty(
        name="asset path",
        description="path of asset to add",
        subtype='FILE_PATH'
    ) # type: ignore

    @classmethod
    def register(cls):
        bpy.types.WindowManager.assets_registry = PointerProperty(type=AssetsRegistry)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.assets_registry


    def add_asset(self, name, type, path, internal): # internal means it cannot be edited by the user, aka auto generated
        in_list = [asset for asset in self.assets_list if (asset["path"] == path)]
        in_list = len(in_list) > 0
        if not in_list:
            self.assets_list.append({"name": name, "type": type, "path": path, "internal": internal})

    def remove_asset(self, path):
        self.assets_list[:] = [asset for asset in self.assets_list if (asset["path"] != path)]
