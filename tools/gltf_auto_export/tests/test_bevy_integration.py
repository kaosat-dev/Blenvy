import bpy
import os 
import subprocess
import json
import pytest
import shutil

@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")

    def finalizer():
        root_path =  "../../testing/bevy_example"
        assets_root_path = os.path.join(root_path, "assets")
        models_path =  os.path.join(assets_root_path, "models")
        #materials_path = os.path.join("../../testing", "materials")
        #other_materials_path = os.path.join("../../testing", "other_materials")

        print("\nPerforming teardown...")
        if os.path.exists(models_path):
            shutil.rmtree(models_path)

        """if os.path.exists(materials_path):
            shutil.rmtree(materials_path)

        if os.path.exists(other_materials_path):
            shutil.rmtree(other_materials_path)"""
        diagnostics_file_path = os.path.join(root_path, "bevy_diagnostics.json")
        if os.path.exists(diagnostics_file_path):
            os.remove(diagnostics_file_path)

    request.addfinalizer(finalizer)

    return None


"""
- removes existing gltf files if needed
- calls exporter on the testing scene
- launches bevy app & checks for output
- if all worked => test is a-ok
"""
def test_export_complex(setup_data):
    root_path = "../../testing/bevy_example"
    assets_root_path = os.path.join(root_path, "assets")
    models_path = os.path.join(assets_root_path, "models")
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # with change detection
    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['World'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    # move the main cube
    bpy.data.objects["Cube"].location = [1, 0, 0]
    # move the cube in the library
    bpy.data.objects["Blueprint1_mesh"].location = [1, 2, 1]

    auto_export_operator(
        direct_mode=True,
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_legacy_mode=False,
        export_animations=True
    )
    # blueprint1 => has an instance, got changed, should export
    # blueprint2 => has NO instance, but marked as asset, should export
    # blueprint3 => has NO instance, not marked as asset, used inside blueprint 4: should export
    # blueprint4 => has an instance, with nested blueprint3, should export
    # blueprint5 => has NO instance, not marked as asset, should NOT export

    assert os.path.exists(os.path.join(models_path, "World.glb")) == True

    assert os.path.exists(os.path.join(models_path, "library", "Blueprint1.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint2.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint3.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint4_nested.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint5.glb")) == False
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint6_animated.glb")) == True
    assert os.path.exists(os.path.join(models_path, "library", "Blueprint7_hierarchy.glb")) == True

    # now run bevy
    bla = "cargo run --features bevy/dynamic_linking"
    # assert getattr(propertyGroup, 'a') == 0.5714026093482971
    FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess
    filename = "my_file.dat"
    args = bla
    #subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False, cwd=bevy_run_exec_path)
    return_code = subprocess.call(["cargo", "run", "--features", "bevy/dynamic_linking"], cwd=root_path)
    print("RETURN CODE OF BEVY APP", return_code)
    assert return_code == 0

    with open(os.path.join(root_path, "bevy_diagnostics.json")) as diagnostics_file:
        diagnostics = json.load(diagnostics_file)
        print("diagnostics", diagnostics)
        assert diagnostics["animations"] == True
        
