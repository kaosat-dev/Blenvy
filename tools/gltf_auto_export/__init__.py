bl_info = {
    "name": "gltf_auto_export",
    "author": "kaosigh",
    "version": (0, 16, 0),
    "blender": (3, 4, 0),
    "location": "File > Import-Export",
    "description": "glTF/glb auto-export",
    "warning": "",
    "wiki_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow",
    "tracker_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow/issues/new",
    "category": "Import-Export"
}
import bpy
from bpy.types import Context
from bpy.props import (StringProperty, BoolProperty, PointerProperty)

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

from io_scene_gltf2 import (GLTF_PT_export_main, GLTF_PT_export_include)

class Testing_PT_MainPanel(bpy.types.Panel):
    bl_idname = "Testing_PT_MainPanel"
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Gltf auto_export"
    bl_context = "objectmode"


    def draw_header(self, context):
        layout = self.layout
        name = context.object.name if context.object != None else ''
        layout.label(text="Gltf auto export ")

    def draw(self, context):
        layout = self.layout
        object = context.object
        collection = context.collection

        layout.label(text="MAKE SURE TO CLICK ON 'REMEMBER EXPORT SETTINGS' !!")
        op = layout.operator("EXPORT_SCENE_OT_gltf", text='Gltf settings')#'glTF 2.0 (.glb/.gltf)')
        #op.export_format = 'GLTF_SEPARATE'
        op.use_selection=True
        op.will_save_settings=True
        op.use_visible=True # Export visible and hidden objects. See Object/Batch Export to skip.
        op.use_renderable=True
        op.use_active_collection = True
        op.use_active_collection_with_nested=True
        op.use_active_scene = True
        op.filepath="dummy"

        #print("GLTF_PT_export_main", GLTF_PT_export_main.bl_parent_id)


# wrapper operator
"""class WrapperOperator(bpy.types.Operator):
    bl_idname = "node.delete"
    bl_label = "Delete"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # unregister wrapper replacement operator
        bpy.utils.unregister_class(DeleteOperator)
        # call original native operator
        bpy.ops.node.delete()
        # register back the wrapper
        bpy.utils.register_class(DeleteOperator)
        return {'FINISHED'}"""


class GLTF_PT_export_main2(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ""
    bl_parent_id = "Testing_PT_MainPanel"
    bl_options = {'HIDE_HEADER'}


    '''@classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENE_OT_gltf"'''

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        """sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'export_format')
        if operator.export_format == 'GLTF_SEPARATE':
            layout.prop(operator, 'export_keep_originals')
            if operator.export_keep_originals is False:
                layout.prop(operator, 'export_texture_dir', icon='FILE_FOLDER')
        if operator.export_format == 'GLTF_EMBEDDED':
            layout.label(text="This is the least efficient of the available forms, and should only be used when required.", icon='ERROR')

        layout.prop(operator, 'export_copyright')
        layout.prop(operator, 'will_save_settings')"""

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

    AutoExportTracker,

    Testing_PT_MainPanel,
    GLTF_PT_export_main2,

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

    bpy.types.WindowManager.was_good_operator = BoolProperty(default=False)
    bpy.types.Scene.was_good_operator = BoolProperty(default=False)

    #GLTF_PT_export_main.bl_parent_id = "Testing_PT_MainPanel"
    #GLTF_PT_export_include.bl_parent_id = "Testing_PT_MainPanel"
    """try:
        bpy.app.timers.unregister(watch_schema)
    except Exception as error:
        print("failed to unregister", error)
        pass"""


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)

    bpy.app.handlers.depsgraph_update_post.remove(post_update)
    bpy.app.handlers.save_post.remove(post_save)

   


if "gltf_auto_export" == "__main__":
    register()
