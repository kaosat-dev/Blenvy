bl_info = {
    "name": "gltf_auto_export",
    "author": "kaosigh",
    "version": (0, 14, 0),
    "blender": (3, 4, 0),
    "location": "File > Import-Export",
    "description": "glTF/glb auto-export",
    "warning": "",
    "wiki_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow",
    "tracker_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow/issues/new",
    "category": "Import-Export"
}
import bpy

from .auto_export.operators import AutoExportGLTF
from .auto_export.tracker import AutoExportTracker
from .auto_export.preferences import (AutoExportGltfAddonPreferences)

from .auto_export.internals import (SceneLink,
                        SceneLinks,
                        CollectionToExport,
                        CollectionsToExport,
                        CUSTOM_PG_sceneName
                        )
from .ui.main import (GLTF_PT_auto_export_main,
                      GLTF_PT_auto_export_root,
                      GLTF_PT_auto_export_blueprints,
                      GLTF_PT_auto_export_collections_list,
                      GLTF_PT_auto_export_gltf,
                      SCENE_UL_GLTF_auto_export,
                      )
from .ui.operators import (SCENES_LIST_OT_actions)


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
from bpy.app.handlers import persistent

@persistent
def post_update(scene, depsgraph):
    bpy.context.window_manager.auto_export_tracker.deps_update_handler( scene, depsgraph)

@persistent
def post_save(scene, depsgraph):
    bpy.context.window_manager.auto_export_tracker.save_handler( scene, depsgraph)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # for some reason, adding these directly to the tracker class in register() do not work reliably
    bpy.app.handlers.depsgraph_update_post.append(post_update)
    bpy.app.handlers.save_post.append(post_save)

    # add our addon to the toolbar
    bpy.types.TOPBAR_MT_file_export.append(menu_func_import)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)

    bpy.app.handlers.depsgraph_update_post.remove(post_update)
    bpy.app.handlers.save_post.remove(post_save)


if "gltf_auto_export" == "__main__":
    register()
