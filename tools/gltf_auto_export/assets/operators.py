import os
import bpy
from bpy_types import (Operator)
from bpy.props import (StringProperty, EnumProperty)

class OT_add_bevy_asset(Operator):
    """Add asset"""
    bl_idname = "bevyassets.add"
    bl_label = "Add bevy asset"
    bl_options = {"UNDO"}

    asset_name: StringProperty(
        name="asset name",
        description="name of asset to add",
    ) # type: ignore

    asset_type: bpy.types.WindowManager.asset_type_selector = EnumProperty(
            items=(
                ('MODEL', "Model", ""),
                ('AUDIO', "Audio", ""),
                ('IMAGE', "Image", ""),
                )
        ) # type: ignore

    asset_path: StringProperty(
        name="asset path",
        description="path of asset to add",
        subtype='FILE_PATH'
    ) # type: ignore

    def execute(self, context):
        context.window_manager.assets_registry.add_asset(self.asset_name, self.asset_type, self.asset_path, False)
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

    def execute(self, context):
        context.window_manager.assets_registry.remove_asset(self.asset_path)
        return {'FINISHED'}