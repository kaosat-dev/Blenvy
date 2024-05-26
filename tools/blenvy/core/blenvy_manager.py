import os
import bpy
from bpy_types import (PropertyGroup)
from bpy.props import (BoolProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty, IntProperty)
from .scene_helpers import SceneSelector
from ..settings import upsert_settings, load_settings, generate_complete_preferences_dict
import blenvy.add_ons.auto_export.settings as auto_export_settings
import blenvy.add_ons.bevy_components.settings as component_settings


# list of settings we do NOT want to save
settings_black_list = ['settings_save_enabled', 'main_scene_selector', 'main_scenes', 'main_scenes_index', 'library_scene_selector', 'library_scenes', 'library_scenes_index',
                       #'project_root_path_full', 'assets_path_full', '' 
                       ]

def save_settings(settings, context):  
    if settings.settings_save_enabled:
        settings_dict =  generate_complete_preferences_dict(settings, BlenvyManager, [])
        print("save settings", settings, context, settings_dict)
        # upsert_settings(settings.settings_save_path, {key: settings_dict[key] for key in settings_dict.keys() if key not in settings_black_list})

def update_scene_lists(blenvy, context):                
    blenvy.main_scene_names = [scene.name for scene in blenvy.main_scenes] # FIXME: unsure
    blenvy.library_scene_names = [scene.name for scene in blenvy.library_scenes] # FIXME: unsure
    upsert_settings(blenvy.settings_save_path, {"common_main_scene_names": [scene.name for scene in blenvy.main_scenes]})
    upsert_settings(blenvy.settings_save_path, {"common_library_scene_names": [scene.name for scene in blenvy.library_scenes]})

def update_asset_folders(blenvy, context):
    asset_path_names = ['project_root_path', 'assets_path', 'blueprints_path', 'levels_path', 'materials_path']
    for asset_path_name in asset_path_names:
        upsert_settings(blenvy.settings_save_path, {asset_path_name: getattr(blenvy, asset_path_name)})

def update_mode(blenvy, context):
    upsert_settings(blenvy.settings_save_path, {"mode": blenvy.mode })

def is_scene_already_in_use(self, scene):
    try:
        return scene.name not in self.main_scenes and scene.name not in self.library_scenes
    except:
        return True

class BlenvyManager(PropertyGroup):

    settings_save_path = ".blenvy_common_settings" # where to store data in bpy.texts
    settings_save_enabled = BoolProperty(name="settings save enabled", default=True)

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

    # computed property for the absolute path of assets
    project_root_path_full: StringProperty(
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.project_root_path))
    ) # type: ignore

    assets_path: StringProperty(
        name='Export folder',
        description='The root folder for all exports(relative to the root folder/path) Defaults to "assets" ',
        default='./assets',
        options={'HIDDEN'},
        update= update_asset_folders
    ) # type: ignore
    
    # computed property for the absolute path of assets
    assets_path_full: StringProperty(
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.project_root_path, self.assets_path))
    ) # type: ignore

    blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to the assets folder)',
        default='blueprints',
        update= update_asset_folders
    ) # type: ignore

    # computed property for the absolute path of blueprints
    blueprints_path_full: StringProperty(
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.project_root_path, self.assets_path, self.blueprints_path))
    ) # type: ignore

    levels_path: StringProperty(
        name='Levels path',
        description='path to export the levels (main scenes) to (relative to the assets folder)',
        default='levels',
        update= update_asset_folders
    ) # type: ignore

    # computed property for the absolute path of blueprints
    levels_path_full: StringProperty(
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.project_root_path, self.assets_path, self.levels_path))
    ) # type: ignore

    materials_path: StringProperty(
        name='Materials path',
        description='path to export the materials libraries to (relative to the assets folder)',
        default='materials',
        update= update_asset_folders
    ) # type: ignore

    # computed property for the absolute path of blueprints
    materials_path_full: StringProperty(
        get=lambda self: os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), self.project_root_path, self.assets_path, self.materials_path))
    ) # type: ignore

    main_scenes: CollectionProperty(name="main scenes", type=SceneSelector) # type: ignore
    main_scenes_index: IntProperty(name = "Index for main scenes list", default = 0, update=update_scene_lists) # type: ignore
    #main_scene_names = [] # FIXME: unsure

    library_scenes: CollectionProperty(name="library scenes", type=SceneSelector) # type: ignore
    library_scenes_index: IntProperty(name = "Index for library scenes list", default = 0, update=update_scene_lists) # type: ignore
    #library_scene_names = [] # FIXME: unsure

    # sub ones
    auto_export: PointerProperty(type=auto_export_settings.AutoExportSettings) # type: ignore
    components: PointerProperty(type=component_settings.ComponentsSettings) # type: ignore

    main_scene_selector: PointerProperty(type=bpy.types.Scene, name="main scene", description="main_scene_picker", poll=is_scene_already_in_use)# type: ignore
    library_scene_selector: PointerProperty(type=bpy.types.Scene, name="library scene", description="library_scene_picker", poll=is_scene_already_in_use)# type: ignore

    @classmethod
    def register(cls):
        bpy.types.WindowManager.blenvy = PointerProperty(type=BlenvyManager)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.blenvy

    def load_settings(self):
        print("LOAD SETTINGS")
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
        
        # now load auto_export settings
        self.auto_export.load_settings()

        # now load component settings
        self.components.load_settings()
