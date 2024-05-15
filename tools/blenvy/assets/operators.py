import os
import json
import bpy
from bpy_types import (Operator)
from bpy.props import (BoolProperty, StringProperty, EnumProperty)

from ..core.path_helpers import absolute_path_from_blend_file
from ..settings import load_settings

class OT_add_bevy_asset(Operator):
    """Add asset"""
    bl_idname = "bevyassets.add"
    bl_label = "Add bevy asset"
    bl_options = {"UNDO"}

    asset_name: StringProperty(
        name="asset name",
        description="name of asset to add",
    ) # type: ignore

    asset_type: EnumProperty(
            items=(
                ('MODEL', "Model", ""),
                ('AUDIO', "Audio", ""),
                ('IMAGE', "Image", ""),
                ('TEXT', "Text", ""),
                )
        ) # type: ignore

    asset_path: StringProperty(
        name="asset path",
        description="path of asset to add",
        subtype='FILE_PATH'
    ) # type: ignore

    # what are we targetting
    target_type: EnumProperty(
        name="target type",
        description="type of the target: scene or blueprint to add an asset to",
        items=(
            ('SCENE', "Scene", ""),
            ('BLUEPRINT', "Blueprint", ""),
            ),
    ) # type: ignore

    target_name: StringProperty(
        name="target name",
        description="name of the target blueprint or scene to add asset to"
    ) # type: ignore

    def execute(self, context):
        assets = []
        blueprint_assets = self.target_type == 'BLUEPRINT'
        if blueprint_assets:
            assets = json.loads(bpy.data.collections[self.target_name].get('assets')) if 'assets' in bpy.data.collections[self.target_name] else []
        else:
            assets = json.loads(bpy.data.scenes[self.target_name].get('assets')) if 'assets' in bpy.data.scenes[self.target_name] else []

        in_list = [asset for asset in assets if (asset["path"] == self.asset_path)]
        in_list = len(in_list) > 0
        if not in_list:
            assets.append({"name": self.asset_name, "type": self.asset_type, "path": self.asset_path, "internal": False})
            # reset controls
            context.window_manager.assets_registry.asset_name_selector = ""
            context.window_manager.assets_registry.asset_type_selector = "MODEL"
            context.window_manager.assets_registry.asset_path_selector = ""

        if blueprint_assets:
            bpy.data.collections[self.target_name]["assets"] = json.dumps(assets)
        else:
            bpy.data.scenes[self.target_name]["assets"] = json.dumps(assets)

        return {'FINISHED'}
    

class OT_remove_bevy_asset(Operator):
    """Remove asset"""
    bl_idname = "bevyassets.remove"
    bl_label = "remove bevy asset"
    bl_options = {"UNDO"}

    asset_path: StringProperty(
        name="asset path",
        description="path of asset to add",
        subtype='FILE_PATH'
    ) # type: ignore


    clear_all: BoolProperty (
        name="clear all assets",
        description="clear all assets",
        default=False
    ) # type: ignore

    # what are we targetting
    target_type: EnumProperty(
        name="target type",
        description="type of the target: scene or blueprint to add an asset to",
        items=(
            ('SCENE', "Scene", ""),
            ('BLUEPRINT', "Blueprint", ""),
            ),
    ) # type: ignore

    target_name: StringProperty(
        name="target name",
        description="name of the target blueprint or scene to add asset to"
    ) # type: ignore


    def execute(self, context):
        assets = []
        blueprint_assets = self.target_type == 'BLUEPRINT'
        if blueprint_assets:
            assets = json.loads(bpy.data.collections[self.target_name].get('assets')) if 'assets' in bpy.data.collections[self.target_name] else []
        else:
            assets = json.loads(bpy.data.scenes[self.target_name].get('assets')) if 'assets' in bpy.data.scenes[self.target_name] else []

        assets = [asset for asset in assets if (asset["path"] != self.asset_path)]
        if blueprint_assets:
            bpy.data.collections[self.target_name]["assets"] = json.dumps(assets)
        else:
            bpy.data.scenes[self.target_name]["assets"] = json.dumps(assets)
        #context.window_manager.assets_registry.remove_asset(self.asset_path)
        return {'FINISHED'}
    

import os
from bpy_extras.io_utils import ImportHelper

class OT_Add_asset_filebrowser(Operator, ImportHelper):
    """Browse for asset files"""
    bl_idname = "asset.open_filebrowser" 
    bl_label = "Select asset file" 

    # Define this to tell 'fileselect_add' that we want a directoy
    filepath: bpy.props.StringProperty(
        name="asset Path",
        description="selected file",
        subtype='FILE_PATH',
        ) # type: ignore
    
    # Filters files
    filter_glob: StringProperty(options={'HIDDEN'}, default='*.jpg;*.jpeg;*.png;*.bmp') # type: ignore

    def execute(self, context):         
        current_auto_settings = load_settings(".gltf_auto_export_settings")
        export_root_path = current_auto_settings.get("export_root_path", "../")
        export_assets_path = current_auto_settings.get("export_assets_path", "assets")
        # FIXME: not sure
        print("export_root_path", export_root_path, "export_assets_path", export_assets_path)
        export_assets_path_absolute = absolute_path_from_blend_file(os.path.join(export_root_path, export_assets_path))

        asset_path = os.path.relpath(self.filepath, export_assets_path_absolute)
        print("asset path", asset_path)

        assets_registry = context.window_manager.assets_registry
        assets_registry.asset_path_selector = asset_path

        print("SELECTED ASSET PATH", asset_path)
        
        return {'FINISHED'}