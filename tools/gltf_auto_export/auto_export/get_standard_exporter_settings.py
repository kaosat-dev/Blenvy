import bpy
import json

def get_standard_exporter_settings():
    standard_gltf_exporter_settings = bpy.data.texts[".gltf_auto_export_gltf_settings"] if ".gltf_auto_export_gltf_settings" in bpy.data.texts else None
    if standard_gltf_exporter_settings != None:
        try:
            standard_gltf_exporter_settings = json.loads(standard_gltf_exporter_settings.as_string())
        except:
            standard_gltf_exporter_settings = {}
    else:
        standard_gltf_exporter_settings = {}
    
    return standard_gltf_exporter_settings