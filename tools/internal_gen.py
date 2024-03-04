import bpy

def test_fake():
    auto_export_operator = bpy.ops.export_scenes.auto_gltf
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] 
    print("OHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    print("export settings", stored_settings.as_string())
    #auto_export_operator(direct_mode = True)