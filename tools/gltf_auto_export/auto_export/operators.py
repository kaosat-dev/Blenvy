import json
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import (IntProperty, StringProperty)
from .preferences import (AutoExportGltfAddonPreferences, AutoExportGltfPreferenceNames)
from ..helpers.helpers_scenes import (get_scenes)
from ..helpers.helpers_collections import (get_exportable_collections)
from .auto_export import auto_export

class AutoExportGLTF(Operator, AutoExportGltfAddonPreferences, ExportHelper):
    """test"""
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

        'export_blueprints',
        'export_blueprints_path',

        'export_marked_assets',
        'collection_instances_combine_mode',
        'export_separate_dynamic_and_static_objects',

        'export_materials_library',
        'export_materials_path',

        'export_scene_settings']

    @classmethod
    def register(cls):
        bpy.types.WindowManager.main_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="main scene", description="main_scene_picker", poll=cls.is_scene_ok)
        bpy.types.WindowManager.library_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="library scene", description="library_scene_picker", poll=cls.is_scene_ok)
        
        bpy.types.WindowManager.main_scenes_list_index = IntProperty(name = "Index for main scenes list", default = 0)
        bpy.types.WindowManager.library_scenes_list_index = IntProperty(name = "Index for library scenes list", default = 0)
        bpy.types.WindowManager.previous_export_settings = StringProperty(default="")

        cls.main_scenes_index = 0
        cls.library_scenes_index = 0

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.main_scene
        del bpy.types.WindowManager.library_scene

        del bpy.types.WindowManager.main_scenes_list_index
        del bpy.types.WindowManager.library_scenes_list_index

        del bpy.types.WindowManager.previous_export_settings

    def is_scene_ok(self, scene):
        try:
            operator = bpy.context.space_data.active_operator
            return scene.name not in operator.main_scenes and scene.name not in operator.library_scenes
        except:
            return True

    def save_settings(self, context):
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
                export_props[k] = v
        # we add main & library scene names to our preferences
        
        export_props['main_scene_names'] = list(map(lambda scene_data: scene_data.name, getattr(self,"main_scenes")))
        export_props['library_scene_names'] = list(map(lambda scene_data: scene_data.name, getattr(self,"library_scenes")))
        self.properties['main_scene_names'] = export_props['main_scene_names']
        self.properties['library_scene_names'] = export_props['library_scene_names']

        stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
        stored_settings.clear()
        stored_settings.write(json.dumps(export_props))
        #print("saving settings", bpy.data.texts[".gltf_auto_export_settings"].as_string(), "raw", json.dumps(export_props))
   
    def load_settings(self, context):
        #print("loading settings")
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

            except (AttributeError, TypeError):
                self.report({"ERROR"}, "Loading export settings failed. Removed corrupted settings")
                bpy.data.texts.remove(bpy.data.texts[".gltf_auto_export_settings"])

    def did_export_settings_change(self):
        previous_export_settings = bpy.data.texts[".gltf_auto_export_gltf_settings"] if ".gltf_auto_export_gltf_settings" in bpy.data.texts else None
        
        # if there was no setting before, it is new, we need export
        if previous_export_settings == None:
            export_settings = {}
            for (k, v) in self.properties.items():
                if k not in AutoExportGltfPreferenceNames:
                    export_settings[k] = v
            export_settings = str(export_settings)
            # the actual gltf export settings, not those of auto export
            stored_export_settings = bpy.data.texts.new(".gltf_auto_export_gltf_settings")
            stored_export_settings.write(export_settings)
            return True
        else:
            export_settings = {}
            for (k, v) in self.properties.items():
                if k in self.white_list or k not in AutoExportGltfPreferenceNames:
                    export_settings[k] = v

            if len(export_settings.keys()) == 0: # first time after we already used the addon, since we already have export settings, but they have not yet been applied
                return False 
            
            export_settings = str(export_settings)
            changed = export_settings != previous_export_settings.as_string()

            previous_export_settings.clear()
            previous_export_settings.write(export_settings)
            return changed

    def execute(self, context):     
        # disable change detection while the operator runs
        bpy.context.window_manager.auto_export_tracker.disable_change_detection()
        if self.direct_mode:
            self.load_settings(context)
        if self.will_save_settings:
            self.save_settings(context)
        
        changes_per_scene = context.window_manager.auto_export_tracker.changed_objects_per_scene
        #determine changed parameters 
        params_changed = self.did_export_settings_change()
        #& do the export
        if self.direct_mode: #Do not auto export when applying settings in the menu, do it on save only
            auto_export(changes_per_scene, params_changed, self)
        # cleanup
        bpy.app.timers.register(bpy.context.window_manager.auto_export_tracker.enable_change_detection, first_interval=1)
        return {'FINISHED'}    
    
    def invoke(self, context, event):
        bpy.context.window_manager.auto_export_tracker.disable_change_detection()
        self.load_settings(context)

        addon_prefs = self
        [main_scene_names, level_scenes, library_scene_names, library_scenes]=get_scenes(addon_prefs)
        (collections, _) = get_exportable_collections(level_scenes, library_scenes, addon_prefs)

        try:
            # we save this list of collections in the context
            bpy.context.window_manager.exportedCollections.clear()
            #TODO: add error handling for this
            for collection_name in collections:
                ui_info = bpy.context.window_manager.exportedCollections.add()
                ui_info.name = collection_name
        except Exception as error:
            self.report({"ERROR"}, "Failed to populate list of exported collections/blueprints")
     
        wm = context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        pass

    def cancel(self, context):
        bpy.app.timers.register(bpy.context.window_manager.auto_export_tracker.enable_change_detection, first_interval=1)
