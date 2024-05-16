import bpy
from bpy_types import (PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, CollectionProperty, IntProperty)
from .scene_helpers import SceneSelector

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

    main_scenes: CollectionProperty(name="main scenes", type=SceneSelector) # type: ignore
    main_scenes_index: IntProperty(name = "Index for main scenes list", default = 0) # type: ignore

    library_scenes: CollectionProperty(name="library scenes", type=SceneSelector) # type: ignore
    library_scenes_index: IntProperty(name = "Index for library scenes list", default = 0) # type: ignore
   
    def is_scene_ok(self, scene):
        try:
            operator = bpy.context.space_data.active_operator
            return scene.name not in operator.main_scenes and scene.name not in operator.library_scenes
        except:
            return True
        
    @classmethod
    def register(cls):
        bpy.types.WindowManager.main_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="main scene", description="main_scene_picker", poll=cls.is_scene_ok)
        bpy.types.WindowManager.library_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="library scene", description="library_scene_picker", poll=cls.is_scene_ok)
        
        bpy.types.WindowManager.main_scenes_list_index = IntProperty(name = "Index for main scenes list", default = 0)
        bpy.types.WindowManager.library_scenes_list_index = IntProperty(name = "Index for library scenes list", default = 0)

        bpy.types.WindowManager.blenvy = PointerProperty(type=BlenvyManager)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.blenvy
        del bpy.types.WindowManager.main_scene
        del bpy.types.WindowManager.library_scene

        del bpy.types.WindowManager.main_scenes_list_index
        del bpy.types.WindowManager.library_scenes_list_index


    def add_asset(self, name, type, path, internal): # internal means it cannot be edited by the user, aka auto generated
      pass

