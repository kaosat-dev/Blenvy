import os
import bpy
from bpy_types import (Operator)
from bpy.props import (StringProperty, EnumProperty)

class OT_switch_bevy_tooling(Operator):
    """Switch bevy tooling"""
    bl_idname = "bevy.tooling_switch"
    bl_label = "Switch bevy tooling"
    bl_options = {"UNDO"}

   
    tool: EnumProperty(
            items=(
                ('COMPONENTS', "Components", ""),
                ('BLUEPRINTS', "Blueprints", ""),
                ('ASSETS', "Assets", ""),
                ('SETTINGS', "Settings", ""),

                )
        ) # type: ignore

  

    def execute(self, context):
        context.window_manager.blenvy.mode = self.tool
        return {'FINISHED'}
    