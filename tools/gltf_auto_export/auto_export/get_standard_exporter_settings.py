import bpy 

def get_standard_exporter_settings():
    for scene in bpy.data.scenes:
        if 'glTF2ExportSettings' in scene:
            print("standard exporter settings", scene['glTF2ExportSettings'])