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
        testing_root_path = "../../testing/tests"
        models_path =  os.path.join(testing_root_path, "models")
        materials_path = os.path.join("../../testing", "materials")
        other_materials_path = os.path.join("../../testing", "other_materials")

        print("\nPerforming teardown...")
        if os.path.exists(models_path):
            shutil.rmtree(models_path)

        if os.path.exists(materials_path):
            shutil.rmtree(materials_path)

        if os.path.exists(other_materials_path):
            shutil.rmtree(other_materials_path)
        

    request.addfinalizer(finalizer)

    return None


def test_export_do_not_export_blueprints(setup_data):
    testing_root_path = "../../testing/tests"
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['Main'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    auto_export_operator(
        direct_mode=True,
        export_output_folder="./tests/models",
        export_scene_settings=True,
        export_blueprints=False,
    )
    assert os.path.exists(os.path.join(testing_root_path, "models", "Main.glb")) == True
    assert os.path.exists(os.path.join(testing_root_path, "models", "library", "Blueprint1.glb")) == False

def test_export_custom_blueprints_path(setup_data):
    testing_root_path = "../../testing/tests"
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['Main'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    auto_export_operator(
        direct_mode=True,
        export_output_folder="./tests/models",
        export_scene_settings=True,
        export_blueprints=True,
        export_blueprints_path = "another_library_path"
    )

    assert os.path.exists(os.path.join(testing_root_path, "models", "another_library_path", "Blueprint1.glb")) == True

def test_export_materials_library(setup_data):
    testing_root_path = "../../testing/tests"
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['Main'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    auto_export_operator(
        direct_mode=True,
        export_output_folder="./tests/models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library = True
    )

    assert os.path.exists(os.path.join(testing_root_path, "models", "library", "Blueprint1.glb")) == True
    assert os.path.exists(os.path.join("../../testing", "materials", "auto_export_template_materials_library.glb")) == True


def test_export_materials_library_custom_path(setup_data):
    testing_root_path = "../../testing/tests"
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['Main'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    auto_export_operator(
        direct_mode=True,
        export_output_folder="./tests/models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library = True,
        export_materials_path="other_materials"
    )

    assert os.path.exists(os.path.join(testing_root_path, "models", "library", "Blueprint1.glb")) == True
    assert os.path.exists(os.path.join("../../testing", "materials", "auto_export_template_materials_library.glb")) == False
    assert os.path.exists(os.path.join("../../testing", "other_materials", "auto_export_template_materials_library.glb")) == True

def test_export_collection_instances_combine_mode(setup_data): # TODO: change & check this
    testing_root_path = "../../testing/tests"
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['Main'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))


    bpy.data.objects["Cube"]["dynamic"] = True

    auto_export_operator(
        direct_mode=True,
        export_output_folder="./tests/models",
        export_blueprints=True,
        collection_instances_combine_mode = 'Embed'
    )

    assert os.path.exists(os.path.join(testing_root_path, "models", "Main.glb")) == True
    assert os.path.exists(os.path.join(testing_root_path, "models", "Main_dynamic.glb")) == False


def test_export_do_not_export_marked_assets(setup_data):
    testing_root_path = "../../testing/tests"
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['Main'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    auto_export_operator(
        direct_mode=True,
        export_output_folder="./tests/models",
        export_scene_settings=True,
        export_blueprints=True,
        export_marked_assets = False
    )
    assert os.path.exists(os.path.join(testing_root_path, "models", "Main.glb")) == True
    assert os.path.exists(os.path.join(testing_root_path, "models", "library", "Blueprint1.glb")) == True
    assert os.path.exists(os.path.join(testing_root_path, "models", "library", "Blueprint2.glb")) == False
    assert os.path.exists(os.path.join(testing_root_path, "models", "library", "Blueprint3.glb")) == False

def test_export_separate_dynamic_and_static_objects(setup_data):
    testing_root_path = "../../testing/tests"
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['Main'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))


    bpy.data.objects["Cube"]["dynamic"] = True

    auto_export_operator(
        direct_mode=True,
        export_output_folder="./tests/models",
        export_scene_settings=True,
        export_blueprints=True,
        export_separate_dynamic_and_static_objects = True
    )

    assert os.path.exists(os.path.join(testing_root_path, "models", "Main.glb")) == True
    assert os.path.exists(os.path.join(testing_root_path, "models", "Main_dynamic.glb")) == True



"""
- removes existing gltf files if needed
- calls exporter on the testing scene
- launches bevy app & checks for output
- if all worked => test is a-ok
"""
def test_export_complex(setup_data):
    testing_root_path = "../../testing/tests"

    #
    print("here", bpy.data.scenes)
    #main_scenes = bpy.data.scenes
    auto_export_operator = bpy.ops.export_scenes.auto_gltf
    # direct export
    """auto_export_operator(
        direct_mode=True,
        export_change_detection=False,
        export_output_folder="./tests/models",
        main_scene_names_compact="Scene"
    )"""


    # with change detection
    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['Main'],
        "library_scene_names": ['Library']
    }
    stored_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_settings.clear()
    stored_settings.write(json.dumps(export_props))

    """auto_export_operator(
        direct_mode=True,
        export_change_detection=True,
        export_output_folder="./tests/models",
        main_scene_names_compact="Scene"
    )"""

    # move the main cube
    bpy.data.objects["Cube"].location = [1, 0, 0]
    # move the cube in the library
    bpy.data.objects["Blueprint1_mesh"].location = [1, 2, 1]

    auto_export_operator(
        direct_mode=True,
        export_output_folder="./tests/models",
        export_scene_settings=True,
        export_blueprints=True
    )
    # blueprint1 => has an instance, got changed, should export
    # blueprint2 => has NO instance, but marked as asset, should export
    # blueprint3 => has NO instance, not marked as asset, should NOT export
    assert os.path.exists(os.path.join(testing_root_path, "models", "Main.glb")) == True
    assert os.path.exists(os.path.join(testing_root_path, "models", "Main_dynamic.glb")) == False

    assert os.path.exists(os.path.join(testing_root_path, "models", "library", "Blueprint1.glb")) == True
    assert os.path.exists(os.path.join(testing_root_path, "models", "library", "Blueprint2.glb")) == True # TODO: also make a test version withouth marked assets export_marked_assets
    assert os.path.exists(os.path.join(testing_root_path, "models", "library", "Blueprint3.glb")) == False

    print("exported stuff")

    # now run bevy
    """bevy_run_exec_path = "../../testing/bevy_registry_export/basic/"
    bla = "cargo run --features bevy/dynamic_linking"
    # assert getattr(propertyGroup, 'a') == 0.5714026093482971
    FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess
    filename = "my_file.dat"
    args = bla
    #subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False, cwd=bevy_run_exec_path)
    subprocess.call(["cargo", "run", "--features", "bevy/dynamic_linking"], cwd=bevy_run_exec_path)"""
