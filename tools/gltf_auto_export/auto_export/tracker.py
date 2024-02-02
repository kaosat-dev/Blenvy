import bpy
from bpy.types import (PropertyGroup)
from bpy.props import (PointerProperty)

from ..internals import CollectionsToExport
from . import auto_export
from ..preferences import (AutoExportGltfPreferenceNames)

class AutoExportTracker(PropertyGroup):

    changed_objects_per_scene = {}
    change_detection_enabled = True
    previous_export_parameters = {}
    export_params_changed = False

    @classmethod
    def register(cls):
        bpy.types.WindowManager.auto_export_tracker = PointerProperty(type=AutoExportTracker)
        # setup handlers for updates & saving
        bpy.app.handlers.save_post.append(cls.save_handler)
        bpy.app.handlers.depsgraph_update_post.append(cls.deps_update_handler)
        # register list of exportable collections
        bpy.types.WindowManager.exportedCollections = bpy.props.CollectionProperty(type=CollectionsToExport)

    @classmethod
    def unregister(cls):
        # remove handlers & co
        try:
            bpy.app.handlers.depsgraph_update_post.remove(cls.deps_update_handler)
        except:pass
        try:
            bpy.app.handlers.save_post.remove(cls.save_handler)
        except:pass
        del bpy.types.WindowManager.auto_export_tracker
        del bpy.types.WindowManager.exportedCollections

    def __init__(self) -> None:
        super().__init__()
        print("INIT")

    @classmethod
    def save_handler(cls, scene, depsgraph):
        print("-------------")
        print("saved", bpy.data.filepath)
        cls.change_detection_enabled = False
        print("changed_objects_per_scene in save", cls.changed_objects_per_scene)

        
        # auto_export(changes_per_scene, export_parameters_changed)
        bpy.ops.export_scenes.auto_gltf(direct_mode= True)


        # (re)set a few things after exporting
        # set the previous export parameters
        #cls.previous_export_parameters = new_export_parameters
        # reset wether the gltf export paramters were changed since the last save 
        cls.export_params_changed = False
        # reset whether there have been changed objects since the last save 
        cls.changed_objects_per_scene.clear()
        # all our logic is done, mark this as done
        cls.change_detection_enabled = True
        print("EXPORT DONE")

    @classmethod
    def deps_update_handler(cls, scene, depsgraph):
        print("change detection enabled", cls.change_detection_enabled)
        if scene.name != "temp_scene": # actually do we care about anything else than the main scene(s) ?
            #print("depsgraph_update_post", scene.name)
            changed_scene = scene.name or ""

            # only deal with changes if we are no in the mids of saving/exporting
            if cls.change_detection_enabled:
                print("-------------")
                if not changed_scene in cls.changed_objects_per_scene:
                    cls.changed_objects_per_scene[changed_scene] = {}

                # depsgraph = bpy.context.evaluated_depsgraph_get()
                for obj in depsgraph.updates:
                    if isinstance(obj.id, bpy.types.Object):
                        # get the actual object
                        object = bpy.data.objects[obj.id.name]
                        print("changed object", obj.id.name)
                        cls.changed_objects_per_scene[scene.name][obj.id.name] = object
                    elif isinstance(obj.id, bpy.types.Material): # or isinstance(obj.id, bpy.types.ShaderNodeTree):
                        # print("changed material", obj.id, "scene", scene.name,)
                        material = bpy.data.materials[obj.id.name]
                        #now find which objects are using the material
                        for obj in bpy.data.objects:
                            for slot in obj.material_slots:
                                if slot.material == material:
                                    cls.changed_objects_per_scene[scene.name][obj.name] = obj

                items = 0
                for scene_name in cls.changed_objects_per_scene:
                    items += len(cls.changed_objects_per_scene[scene_name].keys())
                if items == 0:
                    cls.changed_objects_per_scene.clear()
                #print("changed_objects_per_scene", cls.changed_objects_per_scene)
            else:
                cls.changed_objects_per_scene.clear()

    def disable_change_detection(self,):
        print("disable")
        self.__class__.change_detection_enabled = False
    def enable_change_detection(self):
        print("enable")
        self.__class__.change_detection_enabled = True

def did_export_parameters_change(current_params, previous_params):
    set1 = set(previous_params.items())
    set2 = set(current_params.items())
    difference = dict(set1 ^ set2)
    
    changed_param_names = list(set(difference.keys())- set(AutoExportGltfPreferenceNames))
    changed_parameters = len(changed_param_names) > 0
    return changed_parameters

from ..config import scene_key
"""
def init_settings(addon_prefs):
     # a semi_hack to ensure we have the latest version of the settings
    initialized = bpy.context.window_manager.auto_export_tracker.gltf_auto_export_initialized
    if not initialized:
        print("not initialized, fetching settings if any")
        # semi_hack to restore the correct settings if the add_on was installed before
        settings = bpy.context.scene.get(scene_key)
        if settings:
            print("loading settings in main function")
            try:
                # Update filter if user saved settings
                #if hasattr(self, 'export_format'):
                #    self.filter_glob = '*.glb' if self.export_format == 'GLB' else '*.gltf'
                for (k, v) in settings.items():
                    setattr(addon_prefs, k, v)
                    # inject scenes data
                    if k == 'main_scene_names':
                        main_scenes = addon_prefs.main_scenes
                        for item_name in v:
                            item = main_scenes.add()
                            item.name = item_name

                    if k == 'library_scene_names':
                        library_scenes = addon_prefs.library_scenes
                        for item_name in v:
                            item = library_scenes.add()
                            item.name = item_name

            except Exception as error:
                print("error setting preferences from saved settings", error)
        bpy.context.window_manager.auto_export_tracker.gltf_auto_export_initialized = True"""