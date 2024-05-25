from bpy_types import (Operator)
from bpy.props import (EnumProperty)




class OT_switch_bevy_tooling(Operator):
    """Switch bevy tooling"""
    bl_idname = "bevy.tooling_switch"
    bl_label = "Switch bevy tooling"
    #bl_options = {}

   
    tool: EnumProperty(
            items=(
                ('COMPONENTS', "Components", "Switch to components"),
                ('BLUEPRINTS', "Blueprints", ""),
                ('ASSETS', "Assets", ""),
                ('SETTINGS', "Settings", ""),
                ('TOOLS', "Tools", ""),
                )
        ) # type: ignore

    @classmethod
    def description(cls, context, properties):
        return properties.tool

    def execute(self, context):
        context.window_manager.blenvy.mode = self.tool
        return {'FINISHED'}
    