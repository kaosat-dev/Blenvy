import bpy
from bpy_types import (PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty, StringProperty)


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
    

    export_root_path: StringProperty(
        name = "Project Root Path",
        description="The root folder of your (Bevy) project (not assets!)",
        default='../'
    ) # type: ignore

    export_assets_path: StringProperty(
        name='Export folder',
        description='The root folder for all exports(relative to the root folder/path) Defaults to "assets" ',
        default='./assets',
        options={'HIDDEN'}
    ) # type: ignore

    export_blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to the assets folder)',
        default='blueprints',
    ) # type: ignore

    export_levels_path: StringProperty(
        name='Levels path',
        description='path to export the levels (main scenes) to (relative to the assets folder)',
        default='levels',
    ) # type: ignore

    export_materials_path: StringProperty(
        name='Materials path',
        description='path to export the materials libraries to (relative to the assets folder)',
        default='materials',
    ) # type: ignore
   
    @classmethod
    def register(cls):
        bpy.types.WindowManager.blenvy = PointerProperty(type=BlenvyManager)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.blenvy


    def add_asset(self, name, type, path, internal): # internal means it cannot be edited by the user, aka auto generated
      pass

