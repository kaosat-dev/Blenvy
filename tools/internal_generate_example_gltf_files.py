import bpy

def generate_example_gltf_files(example_path):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] 
    print("export settings", stored_settings)
    """auto_export_operator(
        direct_mode=True,
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_legacy_mode=False,
        export_animations=True
    )"""
    #clear && /home/ckaos/.local/bin/pytest --blender-executable /home/ckaos/tools/blender/blender-4.0.2-linux-x64/blender tests