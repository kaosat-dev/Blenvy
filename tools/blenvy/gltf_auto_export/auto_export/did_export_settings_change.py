import json
import bpy

"""
This should ONLY be run when actually doing exports/aka calling auto_export function, because we only care about the difference in settings between EXPORTS
"""
def did_export_settings_change():
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
        changed = True
    else:
        auto_settings_changed = sorted(json.loads(previous_auto_settings.as_string()).items()) != sorted(json.loads(current_auto_settings.as_string()).items()) if current_auto_settings != None else False
        gltf_settings_changed = sorted(json.loads(previous_gltf_settings.as_string()).items()) != sorted(json.loads(current_gltf_settings.as_string()).items()) if current_gltf_settings != None else False
        
        """print("auto settings previous", sorted(json.loads(previous_auto_settings.as_string()).items()))
        print("auto settings current", sorted(json.loads(current_auto_settings.as_string()).items()))
        print("auto_settings_changed", auto_settings_changed)"""

        """print("gltf settings previous", sorted(json.loads(previous_gltf_settings.as_string()).items()))
        print("gltf settings current", sorted(json.loads(current_gltf_settings.as_string()).items()))
        print("gltf_settings_changed", gltf_settings_changed)"""

        changed = auto_settings_changed or gltf_settings_changed

    return changed