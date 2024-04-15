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
import os
from pathlib import Path
import json
import bpy
from bpy.types import Context
from bpy.props import (StringProperty, BoolProperty, IntProperty, PointerProperty)
import rna_prop_ui


# from .extension import ExampleExtensionProperties, GLTF_PT_UserExtensionPanel, unregister_panel

from .auto_export.operators import AutoExportGLTF
from .auto_export.tracker import AutoExportTracker
from .auto_export.preferences import (AutoExportGltfAddonPreferences)

from .auto_export.internals import (SceneLink,
                        SceneLinks,
                        CollectionToExport,
                        CollectionsToExport,
                        CUSTOM_PG_sceneName
                        )
from .ui.main import (GLTF_PT_auto_export_changes_list, GLTF_PT_auto_export_main,
                      GLTF_PT_auto_export_root,
                      GLTF_PT_auto_export_general,
                      GLTF_PT_auto_export_scenes,
                      GLTF_PT_auto_export_blueprints,
                      GLTF_PT_auto_export_collections_list,
                      SCENE_UL_GLTF_auto_export,

                      GLTF_PT_auto_export_SidePanel
                      )
from .ui.operators import (SCENES_LIST_OT_actions)
from .helpers.ping_depsgraph_update import ping_depsgraph_update
from .helpers.generate_complete_preferences_dict import generate_complete_preferences_dict_gltf


######################################################

"""
# glTF extensions are named following a convention with known prefixes.
# See: https://github.com/KhronosGroup/glTF/tree/main/extensions#about-gltf-extensions
# also: https://github.com/KhronosGroup/glTF/blob/main/extensions/Prefixes.md
glTF_extension_name = "EXT_auto_export"

# Support for an extension is "required" if a typical glTF viewer cannot be expected
# to load a given model without understanding the contents of the extension.
# For example, a compression scheme or new image format (with no fallback included)
# would be "required", but physics metadata or app-specific settings could be optional.
extension_is_required = False

class AutoExportExtensionProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name=bl_info["name"],
        description='Include this extension in the exported glTF file.',
        default=True
        ) # type: ignore

class glTF2ExportUserExtension:

    def __init__(self):
        print("init extension", self)
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension
        self.properties = bpy.context.scene.AutoExportExtensionProperties

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        print("fooo", self)
        if self.properties.enabled:
            if gltf2_object.extensions is None:
                gltf2_object.extensions = {}
            print("bla bla")
            gltf2_object.extensions[glTF_extension_name] = self.Extension(
                name=glTF_extension_name,
                extension={"auto_export_blueprints": self.properties.auto_export_blueprints},
                required=extension_is_required
            )
    def gather_animation_hook():
        pass

    def gather_gltf_hook(self, active_scene_idx, scenes, animations, export_settings):
        if self.properties.enabled:
            print("extension enabled")
        #print("gather_gltf_hook", self, active_scene_idx, scenes, animations, export_settings)"""


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
    GLTF_PT_auto_export_general,
    GLTF_PT_auto_export_scenes,
    GLTF_PT_auto_export_blueprints,
    GLTF_PT_auto_export_SidePanel,
    GLTF_PT_auto_export_collections_list,
    GLTF_PT_auto_export_changes_list,

    AutoExportTracker,
]

def glTF2_pre_export_callback(data):
    #print("pre_export", data)
    pass

def cleanup_file():
    gltf_filepath = "/home/ckaos/projects/bevy/Blender_bevy_components_worklflow/testing/bevy_example/assets/____dummy____.glb"
    if os.path.exists(gltf_filepath):
        os.remove(gltf_filepath)
        return None
    else:
        return 1

def glTF2_post_export_callback(data):
    #print("post_export", data)
    bpy.context.window_manager.auto_export_tracker.export_finished()

    gltf_settings_backup = bpy.context.window_manager.gltf_settings_backup
    gltf_filepath = data["gltf_filepath"]
    gltf_export_id = data['gltf_export_id']
    if gltf_export_id == "gltf_auto_export":
        # some more absurdity: apparently the file is not QUITE done when the export callback is called, so we have to introduce this timer to remove the temporary file correctly
        bpy.context.window_manager.auto_export_tracker.dummy_file_path = gltf_filepath
        try:
            bpy.app.timers.unregister(cleanup_file)
        except:pass
        bpy.app.timers.register(cleanup_file, first_interval=1)

        # get the parameters
        scene = bpy.context.scene
        print(dict(scene))
        if "glTF2ExportSettings" in scene:
            print("write gltf settings")
            settings = scene["glTF2ExportSettings"]
            export_settings = bpy.data.texts[".gltf_auto_export_gltf_settings"] if ".gltf_auto_export_gltf_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_gltf_settings")
            # now write new settings
            export_settings.clear()

            current_gltf_settings = generate_complete_preferences_dict_gltf(dict(settings))
            print("current_gltf_settings", current_gltf_settings)
            export_settings.write(json.dumps(current_gltf_settings))
            print("done writing")
        # now reset the original gltf_settings
        if gltf_settings_backup != "":
            scene["glTF2ExportSettings"] = json.loads(gltf_settings_backup)
        else:
            if "glTF2ExportSettings" in scene:
                del scene["glTF2ExportSettings"]
        bpy.context.window_manager.gltf_settings_backup = ""
       
        # the absurd length one has to go through to RESET THE OPERATOR because it has global state !!!!! AAAAAHHH
        last_operator = bpy.context.window_manager.auto_export_tracker.last_operator
        last_operator.filepath = ""
        last_operator.gltf_export_id = ""

        # AGAIN, something that does not work withouth a timer
        bpy.app.timers.register(ping_depsgraph_update, first_interval=0.1)
       


def menu_func_import(self, context):
    self.layout.operator(AutoExportGLTF.bl_idname, text="glTF auto Export (.glb/gltf)")
from bpy.app.handlers import persistent

@persistent
def post_update(scene, depsgraph):
    bpy.context.window_manager.auto_export_tracker.deps_post_update_handler( scene, depsgraph)

@persistent
def pre_update(scene, depsgraph):
    bpy.context.window_manager.auto_export_tracker.deps_pre_update_handler( scene, depsgraph)

@persistent
def post_save(scene, depsgraph):
    bpy.context.window_manager.auto_export_tracker.save_handler( scene, depsgraph)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # for some reason, adding these directly to the tracker class in register() do not work reliably
    bpy.app.handlers.depsgraph_update_pre.append(pre_update)
    bpy.app.handlers.depsgraph_update_post.append(post_update)
    bpy.app.handlers.save_post.append(post_save)

    # add our addon to the toolbar
    bpy.types.TOPBAR_MT_file_export.append(menu_func_import)
    bpy.types.WindowManager.gltf_settings_backup = StringProperty(default="")

    """bpy.utils.register_class(AutoExportExtensionProperties)
    bpy.types.Scene.AutoExportExtensionProperties = bpy.props.PointerProperty(type=AutoExportExtensionProperties)"""
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)

    bpy.app.handlers.depsgraph_update_pre.remove(pre_update)
    bpy.app.handlers.depsgraph_update_post.remove(post_update)
    bpy.app.handlers.save_post.remove(post_save)

    """bpy.utils.unregister_class(AutoExportExtensionProperties)"""

if "gltf_auto_export" == "__main__":
    register()
