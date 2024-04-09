import json
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import (IntProperty)
from .preferences import (AutoExportGltfAddonPreferences, AutoExportGltfPreferenceNames)
from .auto_export import auto_export

class AutoExportGLTF(Operator, AutoExportGltfAddonPreferences, ExportHelper):
    """auto export gltf"""
    #bl_idname = "object.xxx"
    bl_idname = "export_scenes.auto_gltf"
    bl_label = "Apply settings"
    bl_options = {'PRESET', 'UNDO'}
    # ExportHelper mixin class uses this
    filename_ext = ''

    #list of settings (other than purely gltf settings) whose change should trigger a re-generation of gltf files
    white_list = ['auto_export',
        'export_main_scene_name',
        'export_output_folder',
        'export_library_scene_name',
        'export_change_detection',
        'export_blueprints',
        'export_blueprints_path',

        'export_marked_assets',
        'collection_instances_combine_mode',
        'export_separate_dynamic_and_static_objects',

        'export_materials_library',
        'export_materials_path',

        'export_scene_settings'
        'export_legacy_mode'
        ]

    @classmethod
    def register(cls):
        bpy.types.WindowManager.main_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="main scene", description="main_scene_picker", poll=cls.is_scene_ok)
        bpy.types.WindowManager.library_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="library scene", description="library_scene_picker", poll=cls.is_scene_ok)
        
        bpy.types.WindowManager.main_scenes_list_index = IntProperty(name = "Index for main scenes list", default = 0)
        bpy.types.WindowManager.library_scenes_list_index = IntProperty(name = "Index for library scenes list", default = 0)

        cls.main_scenes_index = 0
        cls.library_scenes_index = 0

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.main_scene
        del bpy.types.WindowManager.library_scene

        del bpy.types.WindowManager.main_scenes_list_index
        del bpy.types.WindowManager.library_scenes_list_index

    def is_scene_ok(self, scene):
        try:
            operator = bpy.context.space_data.active_operator
            return scene.name not in operator.main_scenes and scene.name not in operator.library_scenes
        except:
            return True

    def format_settings(self):
        # find all props to save
        exceptional = [
            # options that don't start with 'export_'  
            'collection_instances_combine_mode',
        ]
        all_props = self.properties
        export_props = {
            x: getattr(self, x) for x in dir(all_props)
            if (x.startswith("export_") or x in exceptional) and all_props.get(x) is not None
        }
        # we inject all that we need, the above is not sufficient
        for (k, v) in self.properties.items():
            if k in self.white_list or k not in AutoExportGltfPreferenceNames:
                value = v
                # FIXME: really weird having to do this
                if k == "collection_instances_combine_mode":
                    value = self.collection_instances_combine_mode
                if k == "export_materials":
                    value = self.export_materials
                export_props[k] = value
        # we add main & library scene names to our preferences
        
        export_props['main_scene_names'] = list(map(lambda scene_data: scene_data.name, getattr(self,"main_scenes")))
        export_props['library_scene_names'] = list(map(lambda scene_data: scene_data.name, getattr(self,"library_scenes")))
        return export_props

    def save_settings(self, context):
        export_props = self.format_settings()
        self.properties['main_scene_names'] = export_props['main_scene_names']
        self.properties['library_scene_names'] = export_props['library_scene_names']

        stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
        stored_settings.clear()
        stored_settings.write(json.dumps(export_props))
        #print("saving settings", bpy.data.texts[".gltf_auto_export_settings"].as_string(), "raw", json.dumps(export_props))
   
    def load_settings(self, context):
        # print("loading settings")
        settings = None
        try:
            settings = bpy.data.texts[".gltf_auto_export_settings"].as_string()
            settings = json.loads(settings)
        except: pass

        self.will_save_settings = False
        if settings:
            #print("loading settings in invoke AutoExportGLTF", settings)
            try:
                for (k, v) in settings.items():
                    #print("loading setting", k, v)
                    setattr(self, k, v)
                self.will_save_settings = True

                # Update filter if user saved settings
                if hasattr(self, 'export_format'):
                    self.filter_glob = '*.glb' if self.export_format == 'GLB' else '*.gltf'

                # inject scenes data
                if hasattr(self, 'main_scene_names'):
                    main_scenes = self.main_scenes
                    main_scenes.clear()
                    for item_name in self.main_scene_names:
                        item = main_scenes.add()
                        item.name = item_name

                if hasattr(self, 'library_scene_names'):
                    library_scenes = self.library_scenes
                    library_scenes.clear()
                    for item_name in self.library_scene_names:
                        item = library_scenes.add()
                        item.name = item_name

            except Exception as error:
                print("error", error)
                self.report({"ERROR"}, "Loading export settings failed. Removed corrupted settings")
                bpy.data.texts.remove(bpy.data.texts[".gltf_auto_export_settings"])

    """
    This should ONLY be run when actually doing exports/aka calling auto_export function, because we only care about the difference in settings between EXPORTS
    """
    def did_export_settings_change(self):
        # compare both the auto export settings & the gltf settings
        previous_auto_settings = bpy.data.texts[".gltf_auto_export_settings_previous"] if ".gltf_auto_export_settings_previous" in bpy.data.texts else None
        previous_gltf_settings = bpy.data.texts[".gltf_auto_export_gltf_settings_previous"] if ".gltf_auto_export_gltf_settings_previous" in bpy.data.texts else None

        current_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else None
        current_gltf_settings = bpy.data.texts[".gltf_auto_export_gltf_settings"] if ".gltf_auto_export_gltf_settings" in bpy.data.texts else None

        #check if params have changed
        
        # if there were no setting before, it is new, we need export
        changed = False
        if previous_auto_settings == None:
            print("previous settings missing, exporting")
            changed = True
        elif previous_gltf_settings == None:
            print("previous gltf settings missing, exporting")
            previous_gltf_settings = bpy.data.texts.new(".gltf_auto_export_gltf_settings_previous")
            previous_gltf_settings.write(json.dumps({}))
            if current_gltf_settings == None:
                current_gltf_settings = bpy.data.texts.new(".gltf_auto_export_gltf_settings")
                current_gltf_settings.write(json.dumps({}))

            changed = True

        else:
            auto_settings_changed = sorted(json.loads(previous_auto_settings.as_string()).items()) != sorted(json.loads(current_auto_settings.as_string()).items()) if current_auto_settings != None else False
            gltf_settings_changed = sorted(json.loads(previous_gltf_settings.as_string()).items()) != sorted(json.loads(current_gltf_settings.as_string()).items()) if current_gltf_settings != None else False
            
            """print("auto settings previous", sorted(json.loads(previous_auto_settings.as_string()).items()))
            print("auto settings current", sorted(json.loads(current_auto_settings.as_string()).items()))
            print("auto_settings_changed", auto_settings_changed)

            print("gltf settings previous", sorted(json.loads(previous_gltf_settings.as_string()).items()))
            print("gltf settings current", sorted(json.loads(current_gltf_settings.as_string()).items()))
            print("gltf_settings_changed", gltf_settings_changed)"""

            changed = auto_settings_changed or gltf_settings_changed
        # now write the current settings to the "previous settings"
        if current_auto_settings != None:
            previous_auto_settings = bpy.data.texts[".gltf_auto_export_settings_previous"] if ".gltf_auto_export_settings_previous" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings_previous")
            previous_auto_settings.clear()
            previous_auto_settings.write(current_auto_settings.as_string()) # TODO : check if this is always valid

        if current_gltf_settings != None:
            previous_gltf_settings = bpy.data.texts[".gltf_auto_export_gltf_settings_previous"] if ".gltf_auto_export_gltf_settings_previous" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_gltf_settings_previous")
            previous_gltf_settings.clear()
            previous_gltf_settings.write(current_gltf_settings.as_string())

        return changed

    def execute(self, context):    
        #print("execute")
        bpy.context.window_manager.auto_export_tracker.disable_change_detection()
        if self.direct_mode:
            self.load_settings(context)
        if self.will_save_settings:
            self.save_settings(context)

        if self.auto_export: # only do the actual exporting if auto export is actually enabled
            changes_per_scene = context.window_manager.auto_export_tracker.changed_objects_per_scene
            #& do the export
            if self.direct_mode: #Do not auto export when applying settings in the menu, do it on save only                
                #determine changed parameters 
                params_changed = self.did_export_settings_change()
                auto_export(changes_per_scene, params_changed, self)
                # cleanup 
                # reset the list of changes in the tracker
                bpy.context.window_manager.auto_export_tracker.clear_changes()
                print("AUTO EXPORT DONE")            
            bpy.app.timers.register(bpy.context.window_manager.auto_export_tracker.enable_change_detection, first_interval=0.1)
        else: 
            print("auto export disabled, skipping")
        return {'FINISHED'}    
    
    def invoke(self, context, event):
        #print("invoke")
        bpy.context.window_manager.auto_export_tracker.disable_change_detection()
        self.load_settings(context)
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        pass

    def cancel(self, context):
        print("cancel")
        #bpy.context.window_manager.auto_export_tracker.enable_change_detection()
        bpy.app.timers.register(bpy.context.window_manager.auto_export_tracker.enable_change_detection, first_interval=1)

