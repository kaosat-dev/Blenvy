import os
import bpy
import subprocess

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
    # blender-template
    #clear && /home/ckaos/.local/bin/pytest --blender-executable /home/ckaos/tools/blender/blender-4.0.2-linux-x64/blender tests


examples = [
    '../examples/bevy_gltf_blueprints/basic',
    '../examples/bevy_gltf_blueprints/animation',
    '../examples/bevy_gltf_blueprints/basic_xpbd_physics',
    '../examples/bevy_gltf_blueprints/materials',
    '../examples/bevy_gltf_blueprints/multiple_levels_multiple_blendfiles',
]

for example_path in examples:
    print("generating gltf files for ", example_path)
    assets_path = os.path.join(example_path, "assets")
    art_path = os.path.join(example_path, "art")
    blend_files = []

    if os.path.exists(assets_path):
        for file in os.listdir(assets_path):
            if file.endswith(".blend"):
                print("file found !", file)
                blend_files.append(os.path.join("assets", file))
    if os.path.exists(art_path):
        for file in os.listdir(art_path):
            if file.endswith(".blend"):
                print("file found !", file)
                blend_files.append(os.path.join("art", file))

    
    print("blend files", blend_files)
    for blend_file in blend_files:
        fake_test_path = os.path.abspath("./internal_gen.py")
        command = "pytest -svv --blender-executable /home/ckaos/tools/blender/blender-4.0.2-linux-x64/blender --blender-template "+blend_file + " "+fake_test_path
        return_code = subprocess.call(command.split(" "), cwd=example_path)
        #generate_example_gltf_files(example_path)