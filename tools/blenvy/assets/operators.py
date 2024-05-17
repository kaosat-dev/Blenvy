import os
import json
import bpy
from bpy_types import (Operator)
from bpy.props import (BoolProperty, StringProperty, EnumProperty)

from .asset_helpers import does_asset_exist, get_user_assets, remove_asset, upsert_asset
from .assets_scan import get_main_scene_assets_tree

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
        target = None
        if blueprint_assets:
            target = bpy.data.collections[self.target_name]
        else:
            target = bpy.data.scenes[self.target_name]
        assets = get_user_assets(target)
        asset = {"name": self.asset_name, "type": self.asset_type, "path": self.asset_path}
        if not does_asset_exist(target, asset):
            upsert_asset(target, asset)

            #assets.append({"name": self.asset_name, "type": self.asset_type, "path": self.asset_path, "internal": False})
            # reset controls
            context.window_manager.assets_registry.asset_name_selector = ""
            context.window_manager.assets_registry.asset_type_selector = "MODEL"
            context.window_manager.assets_registry.asset_path_selector = ""

        """if blueprint_assets:
            bpy.data.collections[self.target_name]["assets"] = json.dumps(assets)
        else:
            bpy.data.scenes[self.target_name]["assets"] = json.dumps(assets)"""

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
            target = bpy.data.collections[self.target_name]
        else:
            target = bpy.data.scenes[self.target_name]
        remove_asset(target, {"path": self.asset_path})
       
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
        project_root_path = current_auto_settings.get("project_root_path", "../")
        assets_path = current_auto_settings.get("assets_path", "assets")
        # FIXME: not sure
        print("project_root_path", project_root_path, "assets_path", assets_path)
        export_assets_path_absolute = absolute_path_from_blend_file(os.path.join(project_root_path, assets_path))

        asset_path = os.path.relpath(self.filepath, export_assets_path_absolute)
        print("asset path", asset_path)

        assets_registry = context.window_manager.assets_registry
        assets_registry.asset_path_selector = asset_path

        print("SELECTED ASSET PATH", asset_path)
        
        return {'FINISHED'}
    


from types import SimpleNamespace


def write_ron_assets_file(level_name, assets_hierarchy, internal_only=False):
    # just for testing, this uses the format of bevy_asset_loader's asset files
    '''
            ({
        "world":File (path: "models/StartLevel.glb"),
        "level1":File (path: "models/Level1.glb"),
        "level2":File (path: "models/Level2.glb"),

        "models": Folder (
            path: "models/library",
        ),
        "materials": Folder (
            path: "materials",
        ),
    })
    '''
    formated_assets = []
    for asset in assets_hierarchy:
        if asset["internal"] or not internal_only:
            bla = f'\n    "{asset["name"]}": File ( path: "{asset["path"]}" ),'
            formated_assets.append(bla)
    with open(f"testing/bevy_example/assets/assets_{level_name}.assets.ron", "w") as assets_file:
        assets_file.write("({")
        assets_file.writelines(formated_assets)
        assets_file.write("\n})")

class OT_test_bevy_assets(Operator):
    """Test assets"""
    bl_idname = "bevyassets.test"
    bl_label = "test bevy assets"
    bl_options = {"UNDO"}

    def execute(self, context):
        blueprints_registry = context.window_manager.blueprints_registry
        blueprints_registry.add_blueprints_data()
        blueprints_data = blueprints_registry.blueprints_data

        settings = {"blueprints_path": "blueprints", "export_gltf_extension": ".glb"}
        settings = SimpleNamespace(**settings)
        for scene in bpy.data.scenes:
                if scene.name != "Library":
                    assets_hierarchy = get_main_scene_assets_tree(scene, blueprints_data, settings)
                    scene["assets"] = json.dumps(assets_hierarchy)
                    write_ron_assets_file(scene.name, assets_hierarchy, internal_only=False)

        return {'FINISHED'}
