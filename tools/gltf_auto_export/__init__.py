bl_info = {
    "name": "gltf_auto_export",
    "author": "kaosigh",
    "version": (0, 8, 0),
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

from bpy.app.handlers import persistent
from bpy.props import (IntProperty)


from . import helpers
from .internals import (SceneLink,
                        SceneLinks,
                        CollectionToExport,
                        CollectionsToExport,
                        CUSTOM_PG_sceneName
                        )
from .auto_export import auto_export
from .preferences import (AutoExportGltfPreferenceNames,
                          AutoExportGltfAddonPreferences
                          )
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

bpy.context.window_manager['changed_objects_per_scene'] = {}
bpy.context.window_manager['previous_params'] = {}
bpy.context.window_manager['__gltf_auto_export_initialized'] = False
bpy.context.window_manager['__gltf_auto_export_gltf_params_changed'] = False
bpy.context.window_manager['__gltf_auto_export_saving'] = False

######################################################
""" there are two places where we load settings for auto_export from:
- in ui/main AutoExportGLTF -> invoke
- in auto_export.py -> auto_export
This is a workaround needed because of the way the settings are stored , perhaps there is a better way to deal with it ? ie by calling the AutoExportGLTF operator from the auto_export function ?
"""


#see here for original gltf exporter infos https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/addons/io_scene_gltf2/__init__.py
@persistent
def deps_update_handler(scene, depsgraph):
    if scene.name != "temp_scene": # actually do we care about anything else than the main scene(s) ?
        print("depsgraph_update_post", scene.name)
        print("-------------")
        changed = scene.name or ""

        # only deal with changes if we are no in the mids of saving/exporting
        #if not bpy.context.window_manager['__gltf_auto_export_saving']:

        # depsgraph = bpy.context.evaluated_depsgraph_get()
        if not 'changed_objects_per_scene' in bpy.context.window_manager:
            bpy.context.window_manager['changed_objects_per_scene'] = {}

        if not changed in bpy.context.window_manager['changed_objects_per_scene']:
            bpy.context.window_manager['changed_objects_per_scene'][changed] = {}
        
        for obj in depsgraph.updates:
            if isinstance(obj.id, bpy.types.Object):
                # get the actual object
                object = bpy.data.objects[obj.id.name]
                print("changed object", obj.id.name)
                bpy.context.window_manager['changed_objects_per_scene'][scene.name][obj.id.name] = object
            elif isinstance(obj.id, bpy.types.Material): # or isinstance(obj.id, bpy.types.ShaderNodeTree):
                print("changed material", obj.id, "scene", scene.name,)
                material = bpy.data.materials[obj.id.name]
                #now find which objects are using the material
                for obj in bpy.data.objects:
                    for slot in obj.material_slots:
                        if slot.material == material:
                            bpy.context.window_manager['changed_objects_per_scene'][scene.name][obj.name] = obj
        
        bpy.context.window_manager.changedScene = changed

@persistent
def save_handler(dummy): 
    print("-------------")
    print("saved", bpy.data.filepath)
    # mark saving as in progress, this is needed to ignore any changes from the depsgraph done during saving
    # bpy.context.window_manager['__gltf_auto_export_saving'] = True

    if not 'changed_objects_per_scene' in bpy.context.window_manager:
        bpy.context.window_manager['changed_objects_per_scene'] = {}
    changes_per_scene =  bpy.context.window_manager['changed_objects_per_scene']

    if not 'previous_params' in bpy.context.window_manager: 
        bpy.context.window_manager['previous_params'] = {}
    
    #determine changed parameters
    addon_prefs = bpy.context.preferences.addons["gltf_auto_export"].preferences

    prefs = {}
    for (k,v) in addon_prefs.items():
        if k not in AutoExportGltfPreferenceNames:
            prefs[k] = v

    previous_params = bpy.context.window_manager['previous_params'] if 'previous_params' in bpy.context.window_manager else {}
    set1 = set(previous_params.items())
    set2 = set(prefs.items())
    difference = dict(set1 ^ set2)
    
    changed_param_names = list(set(difference.keys())- set(AutoExportGltfPreferenceNames))
    changed_parameters = len(changed_param_names) > 0
    # do the export
    auto_export(changes_per_scene, changed_parameters)


    # save the parameters
    # todo add back
    for (k, v) in prefs.items():
        bpy.context.window_manager['previous_params'][k] = v

    # reset a few things after exporting
    # reset wether the gltf export paramters were changed since the last save 
    bpy.context.window_manager['__gltf_auto_export_gltf_params_changed'] = False
    # reset whether there have been changed objects since the last save 
    bpy.context.window_manager['changed_objects_per_scene'] = {}

    # all our logic is done, mark this as done
    #bpy.context.window_manager['__gltf_auto_export_saving'] = False
    print("EXPORT DONE")


def get_changedScene(self):
    return self["changedScene"]

def set_changedScene(self, value):
    self["changedScene"] = value

classes = [
    SceneLink,
    SceneLinks,
    CUSTOM_PG_sceneName,
    SCENE_UL_GLTF_auto_export,
    SCENES_LIST_OT_actions,

    AutoExportGLTF, 
    AutoExportGltfAddonPreferences,

    CollectionToExport,
    CollectionsToExport,

    GLTF_PT_auto_export_main,
    GLTF_PT_auto_export_root,
    GLTF_PT_auto_export_blueprints,
    GLTF_PT_auto_export_collections_list,
    GLTF_PT_auto_export_gltf
]

def menu_func_import(self, context):
    self.layout.operator(AutoExportGLTF.bl_idname, text="glTF auto Export (.glb/gltf)")

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.main_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="main scene", description="main_scene_chooser", poll=is_scene_ok)
    bpy.types.Scene.library_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="library scene", description="library_scene_picker", poll=is_scene_ok)

    # setup handlers for updates & saving
    bpy.app.handlers.depsgraph_update_post.append(deps_update_handler)
    bpy.app.handlers.save_post.append(save_handler)


    bpy.types.WindowManager.changedScene = bpy.props.StringProperty(get=get_changedScene, set=set_changedScene)
    bpy.types.WindowManager.exportedCollections = bpy.props.CollectionProperty(type=CollectionsToExport)

    # add our addon to the toolbar
    bpy.types.TOPBAR_MT_file_export.append(menu_func_import)

    ## just experiments
    bpy.types.Scene.main_scenes_list_index = IntProperty(name = "Index for main scenes list", default = 0)
    bpy.types.Scene.library_scenes_list_index = IntProperty(name = "Index for library scenes list", default = 0)

    """
    mock_main_scenes = []
    main_scenes = bpy.context.preferences.addons["gltf_auto_export"].preferences.main_scenes
    for item_name in mock_main_scenes:
        item = main_scenes.add()
        item.name = item_name
    
    mock_library_scenes = []
    library_scenes = bpy.context.preferences.addons["gltf_auto_export"].preferences.library_scenes
    for item_name in mock_library_scenes:
        item = library_scenes.add()
        item.name = item_name"""

    bpy.context.preferences.addons["gltf_auto_export"].preferences.main_scenes_index = 0
    bpy.context.preferences.addons["gltf_auto_export"].preferences.library_scenes_index = 0

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)

    # remove handlers & co
    bpy.app.handlers.depsgraph_update_post.remove(deps_update_handler)
    bpy.app.handlers.save_post.remove(save_handler)
    
    del bpy.types.WindowManager.changedScene
    del bpy.types.WindowManager.exportedCollections

    del bpy.types.Scene.main_scene
    del bpy.types.Scene.library_scene

    del bpy.types.Scene.main_scenes_list_index
    del bpy.types.Scene.library_scenes_list_index


if "gltf_auto_export" == "__main__":
    register()