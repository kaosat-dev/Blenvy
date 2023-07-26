#TODO: this is not actually in use yet, just use the blender_auto_export_gltf.py file
bl_info = {
    "name": "Test glTF/glb auto-export",
    "author": "kaosigh",
    "version": (0, 1),
    "blender": (3, 4, 0),
    "location": "File > Import-Export",
    "description": "glTF/glb auto-export",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
    }

import bpy

from .blender_auto_export_gltf import TEST_AUTO_OT_gltf
from .blender_auto_export_gltf import deps_update_handler
from .blender_auto_export_gltf import save_handler
from .blender_auto_export_gltf import get_changedScene
from .blender_auto_export_gltf import set_ChangedScene


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(TEST_AUTO_OT_gltf.bl_idname, text="glTF auto Export (.glb/gltf)")


def register():
    bpy.utils.register_class(TEST_AUTO_OT_gltf)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_import)

    bpy.app.handlers.depsgraph_update_post.append(deps_update_handler)
    bpy.app.handlers.save_post.append(save_handler)
    #bpy.types.TOPBAR_MT_file_export.append(menu_func_import)
    bpy.types.Scene.changedScene = bpy.props.StringProperty(get=get_changedScene, set=set_ChangedScene)


def unregister():
    bpy.utils.unregister_class(TEST_AUTO_OT_gltf)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)

    bpy.app.handlers.depsgraph_update_post.remove(deps_update_handler)
    bpy.app.handlers.save_post.remove(save_handler)
    #bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)
    del bpy.types.Scene.changedScene