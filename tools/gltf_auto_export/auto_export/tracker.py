import json
import bpy
from bpy.types import (PropertyGroup)
from bpy.props import (PointerProperty)

from .internals import CollectionsToExport

class AutoExportTracker(PropertyGroup):

    changed_objects_per_scene = {}
    change_detection_enabled = True
    export_params_changed = False

    @classmethod
    def register(cls):
        bpy.types.WindowManager.auto_export_tracker = PointerProperty(type=AutoExportTracker)
        # register list of exportable collections
        bpy.types.WindowManager.exportedCollections = bpy.props.CollectionProperty(type=CollectionsToExport)

        # setup handlers for updates & saving
        #bpy.app.handlers.save_post.append(cls.save_handler)
        #bpy.app.handlers.depsgraph_update_post.append(cls.deps_update_handler)

    @classmethod
    def unregister(cls):
        # remove handlers & co
        """try:
            bpy.app.handlers.depsgraph_update_post.remove(cls.deps_update_handler)
        except:pass
        try:
            bpy.app.handlers.save_post.remove(cls.save_handler)
        except:pass"""
        del bpy.types.WindowManager.auto_export_tracker
        del bpy.types.WindowManager.exportedCollections

    @classmethod
    def save_handler(cls, scene, depsgraph):
        print("-------------")
        print("saved", bpy.data.filepath)
        # auto_export(changes_per_scene, export_parameters_changed)
        bpy.ops.export_scenes.auto_gltf(direct_mode= True)

        # (re)set a few things after exporting
        # reset wether the gltf export paramters were changed since the last save 
        cls.export_params_changed = False
        # reset whether there have been changed objects since the last save 
        cls.changed_objects_per_scene.clear()
        # all our logic is done, mark this as done
        print("EXPORT DONE")


    @classmethod
    def gltf_exporter_handler(cls):
        # FOr some reason, the active operator here is always None, so using a workaround 
        # active_operator = bpy.context.active_operator 
        print("here", bpy.context.window_manager.gltf_exporter_running)
       
        if bpy.context.window_manager.gltf_exporter_running:
            try:
                dummy_file_path = "/home/ckaos/projects/bevy/Blender_bevy_components_worklflow/testing/bevy_example/assets/dummy.glb"

                import os
                if os.path.exists(dummy_file_path):
                    print("dummy file exists, assuming it worked")
                    os.unlink(dummy_file_path)

                    # get the parameters
                    scene = bpy.context.scene
                    if "glTF2ExportSettings" in scene:
                        settings = scene["glTF2ExportSettings"]
                        formatted_settings = dict(settings)

                        export_settings = bpy.data.texts[".gltf_auto_export_gltf_settings"] if ".gltf_auto_export_gltf_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_gltf_settings")
                        
                        #check if params have changed
                        bpy.context.window_manager.gltf_settings_changed = sorted(json.loads(export_settings.as_string()).items()) != sorted(formatted_settings.items())

                        print("gltf NEW settings", formatted_settings, "OLD settings", export_settings, "CHANGED ?", bpy.context.window_manager.gltf_settings_changed)

                        # now write new settings
                        export_settings.clear()
                        export_settings.write(json.dumps(formatted_settings))


                    # now reset the original gltf_settings
                    if getattr(cls, "existing_gltf_settings", None) != None:
                        print("resetting original gltf settings")
                        scene["glTF2ExportSettings"] = cls.existing_gltf_settings
                    else:
                        print("no pre_existing settings")
                        if "glTF2ExportSettings" in scene:
                            del scene["glTF2ExportSettings"]
                    cls.existing_gltf_settings = None
            except:pass
            bpy.context.window_manager.gltf_exporter_running = False
            return None
            

        else:
            try:
                bpy.app.timers.unregister(cls.gltf_exporter_handler)
            except:pass
            return None
        return 1

    @classmethod
    def deps_update_handler(cls, scene, depsgraph):
        # print("change detection enabled", cls.change_detection_enabled)
        active_operator = bpy.context.active_operator
        if active_operator:
            print("Operator", active_operator.bl_label, active_operator.bl_idname, "bla", bpy.context.window_manager.gltf_exporter_running)
            if active_operator.bl_idname == "EXPORT_SCENE_OT_gltf" and not bpy.context.window_manager.gltf_exporter_running:
                print("matching")
                try:
                    bpy.app.timers.unregister(cls.gltf_exporter_handler)
                except:pass
                bpy.app.timers.register(cls.gltf_exporter_handler, first_interval=3)

                # we force saving params
                active_operator.will_save_settings = True

                # we backup any existing gltf export settings, if there where any
                scene = bpy.context.scene
                if "glTF2ExportSettings" in scene:
                    existing_setting = scene["glTF2ExportSettings"]
                    cls.existing_gltf_settings = existing_setting
                bpy.context.window_manager.gltf_exporter_running = True
                

        else:
            if bpy.context.window_manager.gltf_exporter_running:
                bpy.context.window_manager.gltf_exporter_running = False
            """if active_operator.bl_idname == "EXPORT_SCENE_OT_gltf":
                scene = bpy.context.scene
                if "glTF2ExportSettings" in scene:
                    existing_setting = scene["glTF2ExportSettings"]
                    cls.existing_gltf_settings = existing_setting
                print("we just executed the correct operator")
                active_operator.will_save_settings = True
            else:
                import os
                dummy_file_path = "/home/ckaos/projects/bevy/Blender_bevy_components_worklflow/testing/bevy_example/assets/dummy.glb"
                if os.path.exists(dummy_file_path):
                    print("dummy file exists")
                    os.unlink(dummy_file_path)
                    # get the parameters
                    scene = bpy.context.scene
                    settings = scene["glTF2ExportSettings"]
                    print("gltf settings", dict(settings))

                    # now reset the original gltf_settings
                    if hasattr(cls, "existing_gltf_settings"):
                        print("resetting original gltf settings")
                        scene["glTF2ExportSettings"] = cls.existing_gltf_settings
                    else:
                        del scene["glTF2ExportSettings"]"""


        if scene.name != "temp_scene":
            # print("depsgraph_update_post", scene.name)
            changed_scene = scene.name or ""

            # only deal with changes if we are no in the mids of saving/exporting
            if cls.change_detection_enabled:
                #print("-------------")
                if not changed_scene in cls.changed_objects_per_scene:
                    cls.changed_objects_per_scene[changed_scene] = {}

                # depsgraph = bpy.context.evaluated_depsgraph_get()
                for obj in depsgraph.updates:
                    # print("depsgraph update", obj)
                    if isinstance(obj.id, bpy.types.Object):
                        # get the actual object
                        object = bpy.data.objects[obj.id.name]
                        # print("changed object", obj.id.name)
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

        """depsgraph = bpy.context.evaluated_depsgraph_get()
        for update in depsgraph.updates:
            print("update", update)"""

    def disable_change_detection(self,):
        self.change_detection_enabled = False
        self.__class__.change_detection_enabled = False
    def enable_change_detection(self):
        self.change_detection_enabled = True
        self.__class__.change_detection_enabled = True

