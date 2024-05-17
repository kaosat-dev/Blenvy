import json
import bpy
from bpy.types import Operator
#from ..ui.main import GLTF_PT_auto_export_general, GLTF_PT_auto_export_main, GLTF_PT_auto_export_root

from .preferences import (AutoExportGltfAddonPreferences, AutoExportGltfPreferenceNames)
from .auto_export import auto_export
from ..helpers.generate_complete_preferences_dict import generate_complete_preferences_dict_auto

class AutoExportGLTF(Operator, AutoExportGltfAddonPreferences):#, ExportHelper):
    """auto export gltf"""
    #bl_idname = "object.xxx"
    bl_idname = "export_scenes.auto_gltf"
    bl_label = "Apply settings"
    bl_options = {'PRESET'} # we do not add UNDO otherwise it leads to an invisible operation that resets the state of the saved serialized scene, breaking compares for normal undo/redo operations
    # ExportHelper mixin class uses this
    #filename_ext = ''
    #filepath: bpy.props.StringProperty(subtype="FILE_PATH", default="") # type: ignore

    #list of settings (other than purely gltf settings) whose change should trigger a re-generation of gltf files
    white_list = [
        'auto_export',
        'project_root_path',
        'assets_path',
        'change_detection',
        'export_scene_settings',

        'main_scene_names',
        'library_scene_names',

        'export_blueprints',
        'blueprints_path',
        'export_marked_assets',
        'collection_instances_combine_mode',

        'levels_path',
        'export_separate_dynamic_and_static_objects',

        'export_materials_library',
        'materials_path',
        ]

    @classmethod
    def register(cls):
       pass

    @classmethod
    def unregister(cls):
       pass

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
        
        return export_props

    def save_settings(self, context):
        print("save settings")
        auto_export_settings = self.format_settings()
        
        stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
        stored_settings.clear()

        auto_export_settings = generate_complete_preferences_dict_auto(auto_export_settings)
        stored_settings.write(json.dumps(auto_export_settings))
        print("saved settings", auto_export_settings)
        #print("saving settings", bpy.data.texts[".gltf_auto_export_settings"].as_string(), "raw", json.dumps(export_props))
   
    def load_settings(self, context):
        print("loading settings")
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
        else:
            self.will_save_settings = True

    """
    This should ONLY be run when actually doing exports/aka calling auto_export function, because we only care about the difference in settings between EXPORTS
    """
    def did_export_settings_change(self):
        return True
        # compare both the auto export settings & the gltf settings
        previous_auto_settings = bpy.data.texts[".gltf_auto_export_settings_previous"] if ".gltf_auto_export_settings_previous" in bpy.data.texts else None
        previous_gltf_settings = bpy.data.texts[".gltf_auto_export_gltf_settings_previous"] if ".gltf_auto_export_gltf_settings_previous" in bpy.data.texts else None

        current_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else None
        current_gltf_settings = bpy.data.texts[".gltf_auto_export_gltf_settings"] if ".gltf_auto_export_gltf_settings" in bpy.data.texts else None

        #check if params have changed
        
        # if there were no setting before, it is new, we need export
        changed = False
        if previous_auto_settings == None:
            #print("previous settings missing, exporting")
            changed = True
        elif previous_gltf_settings == None:
            #print("previous gltf settings missing, exporting")
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
    
    def did_objects_change(self):
        # FIXME: add it back
        return {}

    def execute(self, context):
        print("execute auto export", context.window_manager.blenvy.auto_export) 
        blenvy = context.window_manager.blenvy
        auto_export_settings = blenvy.auto_export
        bpy.context.window_manager.auto_export_tracker.disable_change_detection()
        if self.direct_mode:
            self.load_settings(context)
        if self.will_save_settings:
            self.save_settings(context)
        #print("self", self.auto_export)
        if auto_export_settings.auto_export: # only do the actual exporting if auto export is actually enabled
            print("auto export")
            #changes_per_scene = context.window_manager.auto_export_tracker.changed_objects_per_scene
            #& do the export
            # determine changed objects
            changes_per_scene = self.did_objects_change()
            # determine changed parameters 
            params_changed = self.did_export_settings_change()
            auto_export(changes_per_scene, params_changed, blenvy)
            # cleanup 
            # reset the list of changes in the tracker
            bpy.context.window_manager.auto_export_tracker.clear_changes()
            print("AUTO EXPORT DONE")            
            bpy.app.timers.register(bpy.context.window_manager.auto_export_tracker.enable_change_detection, first_interval=0.1)
        else: 
            print("auto export disabled, skipping")
        return {'FINISHED'}    
    
    def invoke(self, context, event):
        print("invoke")
        bpy.context.window_manager.auto_export_tracker.disable_change_detection()
        self.load_settings(context)
        return context.window_manager.invoke_props_dialog(self, title="Auto export", width=640)
    
    def cancel(self, context):
        print("cancel")
        #bpy.context.window_manager.auto_export_tracker.enable_change_detection()
        bpy.app.timers.register(bpy.context.window_manager.auto_export_tracker.enable_change_detection, first_interval=1)

