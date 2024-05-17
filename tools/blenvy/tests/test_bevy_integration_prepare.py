import os
import json
import pytest
import bpy

@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")

    root_path =  "../../testing/bevy_example"
    assets_root_path = os.path.join(root_path, "assets")
    blueprints_path =  os.path.join(assets_root_path, "blueprints")
    levels_path =  os.path.join(assets_root_path, "levels")

    models_path =  os.path.join(assets_root_path, "models")
    materials_path = os.path.join(assets_root_path, "materials")
    yield {
        "root_path": root_path, 
        "models_path": models_path,
        "blueprints_path": blueprints_path, 
        "levels_path": levels_path, 
        "materials_path":materials_path 
        }
    
# this runs the external blueprints file 
def test_export_external_blueprints(setup_data):
    root_path = setup_data["root_path"]
    auto_export_operator = bpy.ops.export_scenes.auto_gltf

    # with change detection
    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : [],
        "library_scene_names": ['Library'],
    }
    gltf_settings = {
        "export_animations": True,
        "export_optimize_animation_size": False
    }

    # store settings for the auto_export part
    stored_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_auto_settings.clear()
    stored_auto_settings.write(json.dumps(export_props))

    # and store settings for the gltf part
    stored_gltf_settings = bpy.data.texts[".gltf_auto_export_gltf_settings"] if ".gltf_auto_export_gltf_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_gltf_settings")
    stored_gltf_settings.clear()
    stored_gltf_settings.write(json.dumps(gltf_settings))


    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        project_root_path = os.path.abspath(root_path),
        #blueprints_path = os.path.join("assets", "models", "library"),
        #export_output_folder = os.path.join("assets", "models"), #"./models",
        #levels_path = os.path.join("assets", "models"),

        export_scene_settings=False,
        export_blueprints=True,
        export_materials_library=True,
        export_marked_assets= True
    )

    assert os.path.exists(os.path.join(setup_data["blueprints_path"], "External_blueprint.glb")) == True
    assert os.path.exists(os.path.join(setup_data["blueprints_path"], "External_blueprint2.glb")) == True
    assert os.path.exists(os.path.join(setup_data["blueprints_path"], "External_blueprint3.glb")) == True