import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import (BoolProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

from .auto_export import auto_export

from ..preferences import (AutoExportGltfAddonPreferences, AutoExportGltfPreferenceNames)
from ..helpers_scenes import (get_scenes)
from ..helpers_collections import (get_exportable_collections)

class AutoExportGLTF(Operator, AutoExportGltfAddonPreferences, ExportHelper):
    """test"""
    bl_idname = "export_scenes.auto_gltf"
    bl_label = "Apply settings"
    bl_options = {'PRESET', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ''

    

    # Custom scene property for saving settings
    scene_key = "auto_gltfExportSettings"

 

    export_settings = {}
    previous_export_settings = {}

    @classmethod
    def register(cls):
        bpy.types.Scene.main_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="main scene", description="main_scene_picker", poll=cls._is_scene_ok)
        bpy.types.Scene.library_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="library scene", description="library_scene_picker", poll=cls._is_scene_ok)
        
        bpy.types.Scene.main_scenes_list_index = IntProperty(name = "Index for main scenes list", default = 0)
        bpy.types.Scene.library_scenes_list_index = IntProperty(name = "Index for library scenes list", default = 0)

        cls.main_scenes_index = 0
        cls.library_scenes_index = 0

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.main_scene
        del bpy.types.Scene.library_scene

        del bpy.types.Scene.main_scenes_list_index
        del bpy.types.Scene.library_scenes_list_index

    def __init__(self) -> None:
        super().__init__()        


    def _is_scene_ok(self, scene):
        print("is scene ok", self, scene)
        return True
        #return scene.name not in self.main_scenes and scene.name not in self.library_scenes

    def save_settings(self, context):
        # find all props to save
        exceptional = [
            # options that don't start with 'export_'  
            #'main_scenes',
            #'library_scenes',
            'collection_instances_combine_mode',
        ]
        all_props = self.properties
        export_props = {
            x: getattr(self, x) for x in dir(all_props)
            if (x.startswith("export_") or x in exceptional) and all_props.get(x) is not None
        }
        # we add main & library scene names to our preferences
        export_props['main_scene_names'] = list(map(lambda scene_data: scene_data.name, getattr(self,"main_scenes")))
        export_props['library_scene_names'] = list(map(lambda scene_data: scene_data.name, getattr(self,"library_scenes")))
        self.properties['main_scene_names'] = export_props['main_scene_names']
        self.properties['library_scene_names'] = export_props['library_scene_names']
        context.scene[self.scene_key] = export_props

   
    def did_export_settings_change(self):
        # find all props to save
        exceptional = [
            # options that don't start with 'export_'  
            'main_scenes',
            'library_scenes',
            'collection_instances_combine_mode',
        ]
        all_props = self.properties
        export_props = {
            x: getattr(self, x) for x in dir(all_props)
            if (x.startswith("export_") or x in exceptional) and all_props.get(x) is not None
        }

        previous_export_settings = dict(self.export_settings)
        self.export_settings = {}
        for (k, v) in self.properties.items():
            if k not in AutoExportGltfPreferenceNames:
                print("adding", k, v)
                self.export_settings[k] = v
        print("self.export_settings", self.export_settings, previous_export_settings)
        changed = did_export_parameters_change(self.export_settings, previous_export_settings)
        self.export_settings = previous_export_settings
        return changed

    def execute(self, context):     
        bpy.context.window_manager.auto_export_tracker.disable_change_detection()
        if self.direct_mode:
            self.load_settings(context)
        if self.will_save_settings:
            self.save_settings(context)
        
        changes_per_scene = context.window_manager.auto_export_tracker.changed_objects_per_scene
        print("FOOO", context.window_manager.auto_export_tracker.changed_objects_per_scene)

        #determine changed parameters & do the export
        auto_export(changes_per_scene, self.did_export_settings_change(), self)

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
        # return self.execute(context)
    
    def load_settings(self, context):
        settings = context.scene.get(self.scene_key)
        self.will_save_settings = False
        if settings:
            print("loading settings in invoke AutoExportGLTF")
            try:
                for (k, v) in settings.items():
                    print("loading setting", k, v)
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
                del context.scene[self.scene_key]

    def draw(self, context):
        pass

    def cancel(self, context):
        bpy.app.timers.register(bpy.context.window_manager.auto_export_tracker.enable_change_detection, first_interval=1)


def did_export_parameters_change(current_params, previous_params):
    set1 = set(previous_params.items())
    set2 = set(current_params.items())
    difference = dict(set1 ^ set2)
    
    changed_param_names = list(set(difference.keys())- set(AutoExportGltfPreferenceNames))
    changed_parameters = len(changed_param_names) > 0
    return changed_parameters