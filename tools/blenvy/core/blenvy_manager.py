import bpy
from bpy_types import (PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty)


class BlenvyManager(PropertyGroup):

    mode: EnumProperty(
            items=(
                ('COMPONENTS', "Components", ""),
                ('BLUEPRINTS', "Blueprints", ""),
                ('ASSETS', "Assets", ""),
                ('SETTINGS', "Settings", ""),
                ('TOOLS', "Tools", ""),
                )
        ) # type: ignore
   
    @classmethod
    def register(cls):
        bpy.types.WindowManager.blenvy = PointerProperty(type=BlenvyManager)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.blenvy


    def add_asset(self, name, type, path, internal): # internal means it cannot be edited by the user, aka auto generated
      pass

