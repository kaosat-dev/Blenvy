
from ..auto_export.preferences import AutoExportGltfAddonPreferences
from io_scene_gltf2 import (ExportGLTF2, GLTF_PT_export_main,ExportGLTF2_Base, GLTF_PT_export_include)

def generate_complete_preferences_dict_gltf(settings):
    complete_preferences = {}    
    defaults = {}
    gltf_parameters_to_ignore = ["use_active_collection", "use_active_collection_with_nested", "use_active_scene", "use_selection", "will_save_settings", "gltf_export_id"]
    def filter_out(pair):
        key, value = pair
        if key in gltf_parameters_to_ignore:
            return False
        return True
    
    for k in ExportGLTF2_Base.__annotations__: # we use parameters from the base class of the standard gltf exporter, that contains all relevant parameters
        item = ExportGLTF2_Base.__annotations__[k]
        #print("item", item)
        default = item.keywords.get('default', None)
        #complete_preferences[k] = default
        defaults[k] = default

    for key in list(settings.keys()):
        if key in defaults and settings[key] != defaults[key]: # only write out values different from defaults
            complete_preferences[key] = settings[key]

    complete_preferences = dict(filter(filter_out, dict(complete_preferences).items()))
    return complete_preferences
    
def generate_complete_preferences_dict_auto(settings):
    complete_preferences = {}    
    for k in AutoExportGltfAddonPreferences.__annotations__:
        item = AutoExportGltfAddonPreferences.__annotations__[k]
        default = item.keywords.get('default', None)
        complete_preferences[k] = default
    
    for key in list(settings.keys()):
        complete_preferences[key] = settings[key]
    return complete_preferences
