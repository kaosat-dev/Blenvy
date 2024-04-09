import json
import os
import bpy
import traceback

from .get_collections_to_export import get_collections_to_export

from .export_main_scenes import export_main_scene
from .export_blueprints import check_if_blueprint_on_disk, check_if_blueprints_exist, export_blueprints_from_collections

from ..helpers.helpers_scenes import (get_scenes, )
from ..modules.export_materials import cleanup_materials, export_materials
from ..modules.bevy_scene_components import upsert_scene_components


"""Main function"""
def auto_export(changes_per_scene, changed_export_parameters, addon_prefs):
    # have the export parameters (not auto export, just gltf export) have changed: if yes (for example switch from glb to gltf, compression or not, animations or not etc), we need to re-export everything
    print ("changed_export_parameters", changed_export_parameters)
    
    try:
        # path to the current blend file
        file_path = bpy.data.filepath
        # Get the folder
        folder_path = os.path.dirname(file_path)
        # get the preferences for our addon
        #should we use change detection or not 
        export_change_detection = getattr(addon_prefs, "export_change_detection")

        export_blueprints = getattr(addon_prefs,"export_blueprints")
        export_output_folder = getattr(addon_prefs,"export_output_folder")

        export_materials_library = getattr(addon_prefs,"export_materials_library")
        export_scene_settings = getattr(addon_prefs,"export_scene_settings")

        [main_scene_names, level_scenes, library_scene_names, library_scenes] = get_scenes(addon_prefs)

        print("main scenes", main_scene_names, "library_scenes", library_scene_names)
        print("export_output_folder", export_output_folder)

        if export_scene_settings:
            # inject/ update scene components
            upsert_scene_components(bpy.context.scene, bpy.context.scene.world, main_scene_names)
        #inject/ update light shadow information
        for light in bpy.data.lights:
            enabled = 'true' if light.use_shadow else 'false'
            light['BlenderLightShadows'] = f"(enabled: {enabled}, buffer_bias: {light.shadow_buffer_bias})"

        # export
        if export_blueprints:
            print("EXPORTING")
            # create parent relations for all collections
            (collections, collections_to_export, main_scenes_to_export, library_collections, collections_per_scene, blueprint_hierarchy, export_levels_path, gltf_extension) = get_collections_to_export(folder_path, export_output_folder, changes_per_scene, changed_export_parameters, addon_prefs)

            # since materials export adds components we need to call this before blueprints are exported
            # export materials & inject materials components into relevant objects
            if export_materials_library:
                export_materials(collections, library_scenes, folder_path, addon_prefs)

            # backup current active scene
            old_current_scene = bpy.context.scene
            # backup current selections
            old_selections = bpy.context.selected_objects

            # first export any main/level/world scenes
            if len(main_scenes_to_export) > 0:
                print("export MAIN scenes")
                for scene_name in main_scene_names:
                    # we have more relaxed rules to determine if the main scenes have changed : any change is ok, (allows easier handling of changes, render settings etc)
                    do_export_main_scene = not export_change_detection or changed_export_parameters or scene_name in changes_per_scene.keys() or not check_if_blueprint_on_disk(scene_name, export_levels_path, gltf_extension)
                    if do_export_main_scene:
                        print("     exporting scene:", scene_name)
                        export_main_scene(bpy.data.scenes[scene_name], folder_path, addon_prefs, library_collections)


            # now deal with blueprints/collections
            do_export_library_scene = not export_change_detection or changed_export_parameters or len(collections_to_export) > 0 # export_library_scene_name in changes_per_scene.keys()
            if do_export_library_scene:
                print("export LIBRARY")
                # we only want to go through the library scenes where our collections to export are present
                for (scene_name, collections_to_export)  in collections_per_scene.items():
                    print("     exporting collections from scene:", scene_name)
                    print("     collections to export", collections_to_export)
                    library_scene = bpy.data.scenes[scene_name]
                    export_blueprints_from_collections(collections_to_export, library_scene, folder_path, addon_prefs, blueprint_hierarchy, collections)

            # reset current scene from backup
            bpy.context.window.scene = old_current_scene

            # reset selections
            for obj in old_selections:
                obj.select_set(True)
            if export_materials_library:
                cleanup_materials(collections, library_scenes)

        else:
            for scene_name in main_scene_names:
                export_main_scene(bpy.data.scenes[scene_name], folder_path, addon_prefs, [])

    except Exception as error:
        print(traceback.format_exc())

        def error_message(self, context):
            self.layout.label(text="Failure during auto_export: Error: "+ str(error))

        bpy.context.window_manager.popup_menu(error_message, title="Error", icon='ERROR')


