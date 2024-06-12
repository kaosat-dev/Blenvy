from bpy_types import (Operator)
from bpy.props import (EnumProperty)




class BLENVY_OT_tooling_switch(Operator):
    """Switch bevy tooling"""
    bl_idname = "bevy.tooling_switch"
    bl_label = "Switch bevy tooling"
    #bl_options = {}

    tool: EnumProperty(
            items=(
                ('COMPONENTS', "Components", "Switch to components"),
                ('BLUEPRINTS', "Blueprints", ""),
                ('LEVELS', "Levels", ""),
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
    