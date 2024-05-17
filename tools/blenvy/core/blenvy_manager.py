import bpy
from bpy_types import (PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, CollectionProperty, IntProperty)
from .scene_helpers import SceneSelector
from ..settings import upsert_settings, load_settings
import blenvy.gltf_auto_export.settings as auto_export_settings

def update_scene_lists(self, context):                
    blenvy = self# context.window_manager.blenvy
    blenvy.main_scene_names = [scene.name for scene in blenvy.main_scenes] # FIXME: unsure
    blenvy.library_scene_names = [scene.name for scene in blenvy.library_scenes] # FIXME: unsure
    upsert_settings(blenvy.settings_save_path, {"common_main_scene_names": [scene.name for scene in blenvy.main_scenes]})
    upsert_settings(blenvy.settings_save_path, {"common_library_scene_names": [scene.name for scene in blenvy.library_scenes]})

def update_asset_folders(self, context):
    blenvy = context.window_manager.blenvy
    asset_path_names = ['project_root_path', 'assets_path', 'blueprints_path', 'levels_path', 'materials_path']
    for asset_path_name in asset_path_names:
        upsert_settings(blenvy.settings_save_path, {asset_path_name: getattr(blenvy, asset_path_name)})

def update_mode(self, context):
    blenvy = self # context.window_manager.blenvy
    upsert_settings(blenvy.settings_save_path, {"mode": blenvy.mode })

class BlenvyManager(PropertyGroup):

    settings_save_path = ".blenvy_settings" # where to store data in bpy.texts

    mode: EnumProperty(
        items=(
                ('COMPONENTS', "Components", ""),
                ('BLUEPRINTS', "Blueprints", ""),
                ('ASSETS', "Assets", ""),
                ('SETTINGS', "Settings", ""),
                ('TOOLS', "Tools", ""),
        ),
        update=update_mode
    ) # type: ignore
    

    project_root_path: StringProperty(
        name = "Project Root Path",
        description="The root folder of your (Bevy) project (not assets!)",
        default='../',
        update= update_asset_folders
    ) # type: ignore

    assets_path: StringProperty(
        name='Export folder',
        description='The root folder for all exports(relative to the root folder/path) Defaults to "assets" ',
        default='./assets',
        options={'HIDDEN'},
        update= update_asset_folders
    ) # type: ignore

    blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to the assets folder)',
        default='blueprints',
        update= update_asset_folders
    ) # type: ignore

    levels_path: StringProperty(
        name='Levels path',
        description='path to export the levels (main scenes) to (relative to the assets folder)',
        default='levels',
        update= update_asset_folders
    ) # type: ignore

    materials_path: StringProperty(
        name='Materials path',
        description='path to export the materials libraries to (relative to the assets folder)',
        default='materials',
        update= update_asset_folders
    ) # type: ignore

    main_scenes: CollectionProperty(name="main scenes", type=SceneSelector) # type: ignore
    main_scenes_index: IntProperty(name = "Index for main scenes list", default = 0, update=update_scene_lists) # type: ignore
    main_scene_names = [] # FIXME: unsure

    library_scenes: CollectionProperty(name="library scenes", type=SceneSelector) # type: ignore
    library_scenes_index: IntProperty(name = "Index for library scenes list", default = 0, update=update_scene_lists) # type: ignore
    library_scene_names = [] # FIXME: unsure

    # sub ones
    auto_export: PointerProperty(type=auto_export_settings.AutoExportSettings) # type: ignore
    #components: PointerProperty(type=bevy_component_settings.ComponentSettings) # type: ignore

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
        
        bpy.types.WindowManager.blenvy = PointerProperty(type=BlenvyManager)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.blenvy
        del bpy.types.WindowManager.main_scene
        del bpy.types.WindowManager.library_scene

    def load_settings(self):
        settings = load_settings(self.settings_save_path)
        if settings is not None:
            if "mode" in settings:
                self.mode = settings["mode"]
            if "common_main_scene_names" in settings:
                for main_scene_name in settings["common_main_scene_names"]:
                    added = self.main_scenes.add()
                    added.name = main_scene_name
            if "common_library_scene_names" in settings:
                for main_scene_name in settings["common_library_scene_names"]:
                    added = self.library_scenes.add()
                    added.name = main_scene_name

            asset_path_names = ['project_root_path', 'assets_path', 'blueprints_path', 'levels_path', 'materials_path']
            for asset_path_name in asset_path_names:
                if asset_path_name in settings:
                    setattr(self, asset_path_name, settings[asset_path_name])
