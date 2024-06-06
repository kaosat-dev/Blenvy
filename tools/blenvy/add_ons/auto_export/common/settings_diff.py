import bpy

from blenvy.settings import are_settings_identical, load_settings, upsert_settings

# which settings are specific to auto_export # TODO: can we infer this ?
parameter_names_whitelist_common = [
    # blenvy core
    'project_root_path',
    'assets_path',
    'blueprints_path',
    'levels_path',
    'materials_path',
    'main_scene_names',
    'library_scene_names',
]

parameter_names_whitelist_auto_export = [
    # auto export
    'export_scene_settings',
    'export_blueprints',
    'export_separate_dynamic_and_static_objects',
    'export_materials_library',
    'collection_instances_combine_mode',
    'export_marked_assets'
]

def get_setting_changes():
    print("get setting changes")

    previous_common_settings = load_settings(".blenvy_common_settings_previous")
    current_common_settings = load_settings(".blenvy_common_settings")
    common_settings_changed = not are_settings_identical(previous_common_settings, current_common_settings, white_list=parameter_names_whitelist_common)

    previous_export_settings = load_settings(".blenvy_export_settings_previous")
    current_export_settings = load_settings(".blenvy_export_settings")
    export_settings_changed = not are_settings_identical(previous_export_settings, current_export_settings, white_list=parameter_names_whitelist_auto_export)

    previous_gltf_settings = load_settings(".blenvy_gltf_settings_previous")
    current_gltf_settings = load_settings(".blenvy_gltf_settings")
    print("previous_gltf_settings", previous_gltf_settings, "current_gltf_settings", current_gltf_settings)
    gltf_settings_changed = not are_settings_identical(previous_gltf_settings, current_gltf_settings)

    # write the new settings to the old settings
    upsert_settings(".blenvy_common_settings_previous", current_common_settings, overwrite=True)
    upsert_settings(".blenvy_export_settings_previous", current_export_settings, overwrite=True)
    upsert_settings(".blenvy_gltf_settings_previous", current_gltf_settings, overwrite=True)

    print("common_settings_changed", common_settings_changed,"export_settings_changed", export_settings_changed, "gltf_settings_changed", gltf_settings_changed, )

    # if there were no setting before, it is new, we need export # TODO: do we even need this ? I guess in the case where both the previous & the new one are both none ? very unlikely, but still
    if previous_common_settings is None:
         return True
    if previous_export_settings is None:
         return True
    if previous_gltf_settings is None:
         return True

    return common_settings_changed or gltf_settings_changed or export_settings_changed
