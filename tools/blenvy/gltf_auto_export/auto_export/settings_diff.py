import bpy

from ...settings import are_settings_identical, load_settings

# which settings are specific to auto_export # TODO: can we infer this ?
auto_export_parameter_names = [
    'project_root_path',
    'assets_path',
    'blueprints_path',
    'levels_path',
    'materials_path',
    #'main_scene_names',
    #'library_scene_names',

    'export_scene_settings',
    'export_blueprints',
    'export_separate_dynamic_and_static_objects',
    'export_materials_library',
    'collection_instances_combine_mode',
    'export_marked_assets'
]

def get_setting_changes():
    previous_gltf_settings = load_settings(".blenvy_gltf_settings_previous")
    current_gltf_settings = load_settings(".blenvy_gltf_settings")
    gltf_settings_changed = not are_settings_identical(previous_gltf_settings, current_gltf_settings)

    previous_export_settings = load_settings(".blenvy_export_settings_previous")
    current_export_settings = load_settings(".blenvy_export_settings")
    auto_export_settings_changed = not are_settings_identical(previous_export_settings, current_export_settings)


    return {}

def did_export_settings_change(self):
        return True
        # compare both the auto export settings & the gltf settings
        previous_auto_settings = bpy.data.texts[".gltf_auto_export_settings_previous"] if ".gltf_auto_export_settings_previous" in bpy.data.texts else None
        previous_gltf_settings = bpy.data.texts[".blenvy_gltf_settings_previous"] if ".blenvy_gltf_settings_previous" in bpy.data.texts else None

        current_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else None
        current_gltf_settings = bpy.data.texts[".blenvy_gltf_settings"] if ".blenvy_gltf_settings" in bpy.data.texts else None

        #check if params have changed
        
        # if there were no setting before, it is new, we need export
        changed = False
        if previous_auto_settings == None:
            #print("previous settings missing, exporting")
            changed = True
        elif previous_gltf_settings == None:
            #print("previous gltf settings missing, exporting")
            previous_gltf_settings = bpy.data.texts.new(".blenvy_gltf_settings_previous")
            previous_gltf_settings.write(json.dumps({}))
            if current_gltf_settings == None:
                current_gltf_settings = bpy.data.texts.new(".blenvy_gltf_settings")
                current_gltf_settings.write(json.dumps({}))

            changed = True

        else:
            auto_settings_changed = sorted(json.loads(previous_auto_settings.as_string()).items()) != sorted(json.loads(current_auto_settings.as_string()).items()) if current_auto_settings != None else False
            gltf_settings_changed = sorted(json.loads(previous_gltf_settings.as_string()).items()) != sorted(json.loads(current_gltf_settings.as_string()).items()) if current_gltf_settings != None else False
            
            """print("auto settings previous", sorted(json.loads(previous_auto_settings.as_string()).items()))
            print("auto settings current", sorted(json.loads(current_auto_settings.as_string()).items()))
            print("auto_settings_changed", auto_settings_changed)

            print("gltf settings previous", sorted(json.loads(previous_gltf_settings.as_string()).items()))
            print("gltf settings current", sorted(json.loads(current_gltf_settings.as_string()).items()))
            print("gltf_settings_changed", gltf_settings_changed)"""

            changed = auto_settings_changed or gltf_settings_changed
        # now write the current settings to the "previous settings"
        if current_auto_settings != None:
            previous_auto_settings = bpy.data.texts[".gltf_auto_export_settings_previous"] if ".gltf_auto_export_settings_previous" in bpy.data.texts else bpy.data.texts.new(".gltf_auto_export_settings_previous")
            previous_auto_settings.clear()
            previous_auto_settings.write(current_auto_settings.as_string()) # TODO : check if this is always valid

        if current_gltf_settings != None:
            previous_gltf_settings = bpy.data.texts[".blenvy_gltf_settings_previous"] if ".blenvy_gltf_settings_previous" in bpy.data.texts else bpy.data.texts.new(".blenvy_gltf_settings_previous")
            previous_gltf_settings.clear()
            previous_gltf_settings.write(current_gltf_settings.as_string())

        return changed