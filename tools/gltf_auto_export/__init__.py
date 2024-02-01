bl_info = {
    "name": "gltf_auto_export",
    "author": "kaosigh",
    "version": (0, 10, 0),
    "blender": (3, 4, 0),
    "location": "File > Import-Export",
    "description": "glTF/glb auto-export",
    "warning": "",
    "wiki_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow",
    "tracker_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow/issues/new",
    "category": "Import-Export"
}
import bpy
import os

from bpy.props import (IntProperty)

from .tracker.tracker import AutoExportTracker
from . import helpers
from .internals import (SceneLink,
                        SceneLinks,
                        CollectionToExport,
                        CollectionsToExport,
                        CUSTOM_PG_sceneName
                        )
from .preferences import (AutoExportGltfAddonPreferences)
from .ui.main import (GLTF_PT_auto_export_main,
                      GLTF_PT_auto_export_root,
                      GLTF_PT_auto_export_blueprints,
                      GLTF_PT_auto_export_collections_list,
                      GLTF_PT_auto_export_gltf,
                      SCENE_UL_GLTF_auto_export,
                      AutoExportGLTF
                      )
from .ui.various import (SCENES_LIST_OT_actions)
from .helpers_scenes import (is_scene_ok)


######################################################
""" there are two places where we load settings for auto_export from:
- in ui/main AutoExportGLTF -> invoke
- in auto_export.py -> auto_export
This is a workaround needed because of the way the settings are stored , perhaps there is a better way to deal with it ? ie by calling the AutoExportGLTF operator from the auto_export function ?
"""


#see here for original gltf exporter infos https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/addons/io_scene_gltf2/__init__.py
classes = [
    SceneLink,
    SceneLinks,
    CUSTOM_PG_sceneName,
    SCENE_UL_GLTF_auto_export,
    SCENES_LIST_OT_actions,

    AutoExportGLTF, 
    #AutoExportGltfAddonPreferences,

    CollectionToExport,
    CollectionsToExport,

    GLTF_PT_auto_export_main,
    GLTF_PT_auto_export_root,
    GLTF_PT_auto_export_blueprints,
    GLTF_PT_auto_export_collections_list,
    GLTF_PT_auto_export_gltf,

    AutoExportTracker
]

def menu_func_import(self, context):
    self.layout.operator(AutoExportGLTF.bl_idname, text="glTF auto Export (.glb/gltf)")

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.main_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="main scene", description="main_scene_chooser", poll=is_scene_ok)
    bpy.types.Scene.library_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="library scene", description="library_scene_picker", poll=is_scene_ok)

    # add our addon to the toolbar
    bpy.types.TOPBAR_MT_file_export.append(menu_func_import)

    ## just experiments
    bpy.types.Scene.main_scenes_list_index = IntProperty(name = "Index for main scenes list", default = 0)
    bpy.types.Scene.library_scenes_list_index = IntProperty(name = "Index for library scenes list", default = 0)

    #bpy.context.preferences.addons["gltf_auto_export"].preferences.main_scenes_index = 0
    #bpy.context.preferences.addons["gltf_auto_export"].preferences.library_scenes_index = 0

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)

    del bpy.types.Scene.main_scene
    del bpy.types.Scene.library_scene

    del bpy.types.Scene.main_scenes_list_index
    del bpy.types.Scene.library_scenes_list_index


if "gltf_auto_export" == "__main__":
    register()