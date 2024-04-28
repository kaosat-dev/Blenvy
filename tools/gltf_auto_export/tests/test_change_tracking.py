import bpy
import os 
import json
import pytest
import shutil
import pathlib
import mathutils

@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")
    #other_materials_path = os.path.join("../../testing", "other_materials")
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
    
    def finalizer():
        print("\nPerforming teardown...")
        if os.path.exists(blueprints_path):
            shutil.rmtree(blueprints_path)

        if os.path.exists(levels_path):
            shutil.rmtree(levels_path)

        if os.path.exists(models_path):
            shutil.rmtree(models_path)

        if os.path.exists(materials_path):
            shutil.rmtree(materials_path)

        diagnostics_file_path = os.path.join(root_path, "bevy_diagnostics.json")
        if os.path.exists(diagnostics_file_path):
            os.remove(diagnostics_file_path)
        
        hierarchy_file_path = os.path.join(root_path, "bevy_hierarchy.json")
        if os.path.exists(hierarchy_file_path):
            os.remove(hierarchy_file_path)

        screenshot_observed_path = os.path.join(root_path, "screenshot.png")
        if os.path.exists(screenshot_observed_path):
            os.remove(screenshot_observed_path)

    request.addfinalizer(finalizer)

    return None


def prepare_auto_export(auto_export_overrides={}):

    # with change detection
    # first, configure things
    # we use the global settings for that
    export_props = {
        "main_scene_names" : ['World'],
        "library_scene_names": ['Library'],
        **auto_export_overrides
    }
  
    # store settings for the auto_export part
    stored_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings")
    stored_auto_settings.clear()
    stored_auto_settings.write(json.dumps(export_props))

    gltf_settings = {
        "export_animations": False,
        "export_optimize_animation_size": False
    }
    # and store settings for the gltf part
    stored_gltf_settings = bpy.data.texts[".gltf_auto_export_gltf_settings"] if ".gltf_auto_export_gltf_settings" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_gltf_settings")
    stored_gltf_settings.clear()
    stored_gltf_settings.write(json.dumps(gltf_settings))

def run_auto_export(setup_data):
    auto_export_operator = bpy.ops.export_scenes.auto_gltf
    auto_export_operator(
        auto_export=True,
        direct_mode=True,
        export_root_folder = os.path.abspath(setup_data["root_path"]),
        export_output_folder="./models",
        export_scene_settings=True,
        export_blueprints=True,
        export_materials_library=False
    )

    levels_path = setup_data["levels_path"]
    level_file_paths = list(map(lambda file_name: os.path.join(levels_path, file_name), sorted(os.listdir(levels_path)))) if os.path.exists(levels_path) else []

    blueprints_path = setup_data["blueprints_path"]
    blueprints_file_paths = list(map(lambda file_name: os.path.join(blueprints_path, file_name), sorted(os.listdir(blueprints_path)))) if os.path.exists(blueprints_path) else []

    modification_times = list(map(lambda file_path: os.path.getmtime(file_path), blueprints_file_paths + level_file_paths))
    # assert os.path.exists(world_file_path) == True

    mapped_files_to_timestamps_and_index = {}
    for (index, file_path) in enumerate(blueprints_file_paths + level_file_paths):
        file_path = pathlib.Path(file_path).stem
        mapped_files_to_timestamps_and_index[file_path] = (modification_times[index], index)

    return (modification_times, mapped_files_to_timestamps_and_index)

def run_auto_export_and_compare(setup_data, changes, expected_changed_files = []):
    (modification_times_first, mapped ) = run_auto_export(setup_data)   
    for index, change in enumerate(changes):
        change()
        (modification_times, mapped ) = run_auto_export(setup_data)   

        changed_files = expected_changed_files[index]
        changed_file_indices =  [mapped[changed_file][1] for changed_file in changed_files]
        #print("changed files", changed_files, changed_file_indices, "mapped", mapped)
        other_files_modification_times = [value for index, value in enumerate(modification_times) if index not in changed_file_indices]
        other_files_modification_times_first = [value for index, value in enumerate(modification_times_first) if index not in changed_file_indices]

        print("other_files_modification_times_new  ", other_files_modification_times)
        print("other_files_modification_times_first", other_files_modification_times_first)
        for changed_file_index in changed_file_indices:
            #print("modification_times_new  [changed_file_index]", modification_times[changed_file_index])
            #print("modification_times_first[changed_file_index]", modification_times_first[changed_file_index])
            if changed_file_index in modification_times_first and changed_file_index in modification_times:
                assert modification_times[changed_file_index] != modification_times_first[changed_file_index], f"failure in change: {index}, at file {changed_file_index}"
            # TODO: we should throw an error in the "else" case ?
        assert other_files_modification_times == other_files_modification_times_first ,  f"failure in change: {index}"
        
        # reset the comparing 
        modification_times_first = modification_times

def test_export_change_tracking_custom_properties(setup_data):
    # set things up
    prepare_auto_export()

    def first_change():
        # now add a custom property to the cube in the main scene & export again
        print("----------------")
        print("main scene change (custom property)")
        print("----------------")
        bpy.data.objects["Cube"]["test_property"] = 42

    run_auto_export_and_compare(
        setup_data=setup_data,
        changes=[first_change],
        expected_changed_files = [["World"]]    # only the "world" file should have changed
    )

def test_export_change_tracking_custom_properties_collection_instances_combine_mode_embed(setup_data):
    # set things up
    prepare_auto_export({"collection_instances_combine_mode": "Embed"})

    def first_change():
        # we have no change, but we also have no blueprints exported, because of the embed mode
        blueprint1_file_path = os.path.join(setup_data["blueprints_path"], "Blueprint1.glb")
        assert os.path.exists(blueprint1_file_path) == False

    def second_change():
        # add a custom property to the cube in the library scene & export again
        # this should trigger changes in the main scene as well since the mode is embed & this blueprints has an instance in the main scene
        print("----------------")
        print("library change (custom property)")
        print("----------------")
        bpy.data.objects["Blueprint1_mesh"]["test_property"] = 42

    def third_change():
        # now we set the _combine mode of the instance to "split", so auto_export should:
        # * not take the changes into account in the main scene
        # * export the blueprint (so file for Blueprint1 will be changed)
        bpy.data.objects["Blueprint1"]["_combine"] = "Split"

    def fourth_change():
        print("----------------")
        print("library change (custom property, forced 'Split' combine mode )")
        print("----------------")

        bpy.data.objects["Blueprint1_mesh"]["test_property"] = 151

    run_auto_export_and_compare(
        setup_data=setup_data,
        changes=[first_change, second_change, third_change, fourth_change],
        expected_changed_files = [[], ["World"], ["World"], ["World"]]    # only the "world" file should have changed
    )


def test_export_change_tracking_light_properties(setup_data):
    # set things up
    prepare_auto_export()

    def first_change():
        # now add a custom property to the cube in the main scene & export again
        print("----------------")
        print("main scene change (light, energy)")
        print("----------------")

        bpy.data.lights["Light"].energy = 100
        #world_file_path = os.path.join(setup_data["levels_path"], "World.glb")
        #assert os.path.exists(world_file_path) == True

    def second_change():
        print("----------------")
        print("main scene change (light, shadow_cascade_count)")
        print("----------------")

        bpy.data.lights["Light"].shadow_cascade_count = 2

    def third_change():
        print("----------------")
        print("main scene change (light, use_shadow)")
        print("----------------")

        bpy.data.lights["Light"].use_shadow = False

    run_auto_export_and_compare(
        setup_data=setup_data,
        changes=[first_change, second_change, third_change],
        expected_changed_files = [["World"], ["World"], ["World"]]    # only the "world" file should have changed
    )


def test_export_change_tracking_camera_properties(setup_data):
    # set things up
    prepare_auto_export()

    def first_change():
        print("----------------")
        print("main scene change (camera)")
        print("----------------")

        bpy.data.cameras["Camera"].angle = 0.5

    run_auto_export_and_compare(
        setup_data=setup_data,
        changes=[first_change],
        expected_changed_files = [["World"]]    # only the "world" file should have changed
    )

def test_export_change_tracking_material_properties(setup_data):
    # set things up
    prepare_auto_export()

    def first_change():
        print("----------------")
        print("main scene change (material, clip)")
        print("----------------")

        bpy.data.materials["Material.001"].blend_method = 'CLIP'
    
    def second_change():
        print("----------------")
        print("main scene change (material, alpha_threshold)")
        print("----------------")
        bpy.data.materials["Material.001"].alpha_threshold = 0.2

    def third_change():
        print("----------------")
        print("main scene change (material, diffuse_color)")
        print("----------------")
        bpy.data.materials["Material.001"].diffuse_color[0] = 0.2

    run_auto_export_and_compare(
        setup_data=setup_data,
        changes=[first_change, second_change, third_change],
        expected_changed_files = [["Blueprint1", "Blueprint7_hierarchy"], ["Blueprint1", "Blueprint7_hierarchy"], ["Blueprint1", "Blueprint7_hierarchy"]]    
        # the material is assigned to Blueprint 1 so in normal (split mode) only the "Blueprint1" file should have changed
        # the same material is assigned to Blueprint 7 so in normal (split mode) only the "Blueprint1" file should have changed
    )


"""
- setup gltf parameters & auto_export parameters
- calls exporter on the testing scene
- saves timestamps of generated files
- changes things in the main scene and/or library
- checks if timestamps have changed
- if all worked => test is a-ok
- removes generated files

"""
def test_export_various_chained_changes(setup_data):

    def first_change():
        # export again with no changes
        print("----------------")
        print("no changes")
        print("----------------")
        world_file_path = os.path.join(setup_data["levels_path"], "World.glb")
        assert os.path.exists(world_file_path) == True
    
    def second_change():
        # now move the main cube & export again
        print("----------------")
        print("main scene change")
        print("----------------")

        bpy.context.window_manager.auto_export_tracker.enable_change_detection() # FIXME: should not be needed, but ..
        bpy.data.objects["Cube"].location = [1, 0, 0]

    def third_change():
        # now same, but move the cube in the library
        print("----------------")
        print("library change (blueprint) ")
        print("----------------")
        bpy.context.window_manager.auto_export_tracker.enable_change_detection() # FIXME: should not be needed, but ..

        bpy.data.objects["Blueprint1_mesh"].location = [1, 2, 1]

    def fourth_change():
        # now change something in a nested blueprint
        print("----------------")
        print("library change (nested blueprint) ")
        print("----------------")

        bpy.data.objects["Blueprint3_mesh"].location= [0, 0.1 ,2]
    
    def fifth_change():
        # now same, but using an operator
        print("----------------")
        print("change using operator")
        print("----------------")

        with bpy.context.temp_override(active_object=bpy.data.objects["Cube"], selected_objects=[bpy.data.objects["Cube"]], scene=bpy.data.scenes["World"]):
            print("translate using operator")
            bpy.ops.transform.translate(value=mathutils.Vector((2.0, 1.0, -5.0)))
            bpy.ops.transform.rotate(value=0.378874, constraint_axis=(False, False, True), mirror=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
            bpy.ops.object.transform_apply()
            bpy.ops.transform.translate(value=(3.5, 0, 0), constraint_axis=(True, False, False))

    run_auto_export_and_compare(
        setup_data=setup_data,
        changes=[first_change, second_change, third_change, fourth_change, fifth_change],
        expected_changed_files = [
            [], 
            ["World"], # only the "world" file should have changed
            ["Blueprint1"],# The blueprint1 file should have changed, since that is the collection we changed, not the world, since we are in "split mode by default"
            ["Blueprint3"],# The blueprint3 file should have changed, since that is the collection we changed # the blueprint4 file NOT, since, while it contains an instance of the collection we changed, the default export mode is "split"
            ["World"]
        ]    
    )

    #bpy.context.window_manager.auto_export_tracker.enable_change_detection() # FIXME: should not be needed, but ..
