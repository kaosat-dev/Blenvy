import copy
import json
import os
from types import SimpleNamespace
import bpy
import traceback

from .preferences import AutoExportGltfAddonPreferences

from .get_collections_to_export import get_collections_to_export
from .get_levels_to_export import get_levels_to_export
from .get_standard_exporter_settings import get_standard_exporter_settings

from .export_main_scenes import export_main_scene
from .export_blueprints import check_if_blueprint_on_disk, check_if_blueprints_exist, export_blueprints_from_collections

from ..helpers.helpers_scenes import (get_scenes, )
from ..modules.export_materials import cleanup_materials, export_materials
from ..modules.bevy_scene_components import upsert_scene_components


"""this is the main 'central' function for all auto export """
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
        export_models_path = os.path.join(folder_path, export_output_folder)

        export_materials_library = getattr(addon_prefs,"export_materials_library")
        export_scene_settings = getattr(addon_prefs,"export_scene_settings")

        # standard gltf export settings are stored differently
        standard_gltf_exporter_settings = get_standard_exporter_settings()
        gltf_extension = standard_gltf_exporter_settings.get("export_format", 'GLB')
        gltf_extension = '.glb' if gltf_extension == 'GLB' else '.gltf'

        # here we do a bit of workaround by creating an override # TODO: do this at the "UI" level
        export_blueprints_path = os.path.join(folder_path, export_output_folder, getattr(addon_prefs,"export_blueprints_path")) if getattr(addon_prefs,"export_blueprints_path") != '' else folder_path
        #print('addon_prefs', AutoExportGltfAddonPreferences.__annotations__)#)addon_prefs.__annotations__)
        if hasattr(addon_prefs, "__annotations__") :
            tmp = {}
            for k in AutoExportGltfAddonPreferences.__annotations__:
                item = AutoExportGltfAddonPreferences.__annotations__[k]
                #print("tutu",k, item.keywords.get('default', None) )
                default = item.keywords.get('default', None)
                tmp[k] = default
            
            for (k, v) in addon_prefs.properties.items():
                tmp[k] = v

            addon_prefs = SimpleNamespace(**tmp) #copy.deepcopy(addon_prefs)
            addon_prefs.__annotations__ = tmp
        addon_prefs.export_blueprints_path = export_blueprints_path
        addon_prefs.export_gltf_extension = gltf_extension
        addon_prefs.export_models_path = export_models_path

        [main_scene_names, level_scenes, library_scene_names, library_scenes] = get_scenes(addon_prefs)

        print("main scenes", main_scene_names, "library_scenes", library_scene_names)
        print("export_output_folder", export_output_folder)

        analysis_experiment(level_scenes, library_scenes)


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
            # get blueprints/collections infos
            (collections, collections_to_export, library_collections, collections_per_scene) = get_collections_to_export(changes_per_scene, changed_export_parameters, addon_prefs)
             
            # get level/main scenes infos
            (main_scenes_to_export) = get_levels_to_export(changes_per_scene, changed_export_parameters, collections, addon_prefs)

            # since materials export adds components we need to call this before blueprints are exported
            # export materials & inject materials components into relevant objects
            if export_materials_library:
                export_materials(collections, library_scenes, folder_path, addon_prefs)

            # update the list of tracked exports
            exports_total = len(collections_to_export) + len(main_scenes_to_export) + (1 if export_materials_library else 0)
            bpy.context.window_manager.auto_export_tracker.exports_total = exports_total
            bpy.context.window_manager.auto_export_tracker.exports_count = exports_total

            print("-------------------------------")
            #print("collections:               all:", collections)
            #print("collections:           changed:", changed_collections)
            #print("collections: not found on disk:", collections_not_on_disk)
            print("collections:        in library:", library_collections)
            print("collections:         to export:", collections_to_export)
            print("collections:         per_scene:", collections_per_scene)
            print("-------------------------------")
            print("BLUEPRINTS:          to export:", collections_to_export)
            print("-------------------------------")
            print("MAIN SCENES:         to export:", main_scenes_to_export)
            print("-------------------------------")
            # backup current active scene
            old_current_scene = bpy.context.scene
            # backup current selections
            old_selections = bpy.context.selected_objects

            # first export any main/level/world scenes
            if len(main_scenes_to_export) > 0:
                print("export MAIN scenes")
                for scene_name in main_scenes_to_export:
                    print("     exporting scene:", scene_name)
                    export_main_scene(bpy.data.scenes[scene_name], folder_path, addon_prefs, library_collections)

            # now deal with blueprints/collections
            do_export_library_scene = not export_change_detection or changed_export_parameters or len(collections_to_export) > 0
            if do_export_library_scene:
                print("export LIBRARY")
                # we only want to go through the library scenes where our collections to export are present
                for (scene_name, collections_to_export)  in collections_per_scene.items():
                    print("     exporting collections from scene:", scene_name)
                    print("     collections to export", collections_to_export)
                    export_blueprints_from_collections(collections_to_export, folder_path, addon_prefs, collections)

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




class Blueprint:
    def __init__(self, name):
        self.name = name
        self.local = True
        self.scene = "" # Not sure, could be usefull for tracking

        self.instances = []
        self.objects = []
        self.nested_blueprints = []

        self.collection = None # should we just sublclass ?
    
    def __repr__(self):
        return f'Name: {self.name} Local: {self.local} Instances: {self.instances},  Objects: {self.objects}, nested_blueprints: {self.nested_blueprints}'

    def __str__(self):
        return f'Name: "{self.name}", Local: {self.local}, Instances: {self.instances},  Objects: {self.objects}, nested_blueprints: {self.nested_blueprints}'



# blueprints: any collection with either
# - an instance
# - marked as asset
# - with the "auto_export" flag
# https://blender.stackexchange.com/questions/167878/how-to-get-all-collections-of-the-current-scene
def analysis_experiment(main_scenes, library_scenes):
    export_marked_assets = True

    blueprints = {}
    blueprints_from_objects = {}
    collections = []

    blueprints_candidates = {}


    # main scenes
    blueprint_instances_per_main_scene = {}
    internal_collection_instances = {}
    external_collection_instances = {}

    for scene in main_scenes:# should it only be main scenes ? what about collection instances inside other scenes ?
        print("scene", scene)
        for object in scene.objects:
            print("object", object.name)
            if object.instance_type == 'COLLECTION':
                collection = object.instance_collection
                collection_name = object.instance_collection.name
                print("  from collection:", collection_name)

                collection_from_library = False
                for scene in library_scenes: # should be only in library scenes
                    collection_from_library = scene.user_of_id(collection) > 0 # TODO: also check if it is an imported asset
                    if collection_from_library:
                        break

                collection_category = internal_collection_instances if collection_from_library else external_collection_instances 
                if not collection_name in collection_category.keys():
                    print("ADDING INSTANCE OF", collection_name, "object", object.name, "categ", collection_category)
                    collection_category[collection_name] = [] #.append(collection_name)
                collection_category[collection_name].append(object)
                if not collection_from_library:
                    for property_name in object.keys():
                        print("stuff", property_name)
                    for property_name in collection.keys():
                        print("OTHER", property_name)

                # blueprints[collection_name].instances.append(object)

                # FIXME: this only account for direct instances of blueprints, not for any nested blueprint inside a blueprint
                if scene.name not in blueprint_instances_per_main_scene.keys():
                    blueprint_instances_per_main_scene[scene.name] = []
                blueprint_instances_per_main_scene[scene.name].append(collection_name)
                
                """# add any indirect ones
                # FIXME: needs to be recursive, either here or above
                for nested_blueprint in blueprints[collection_name].nested_blueprints:
                    if not nested_blueprint in blueprint_instances_per_main_scene[scene.name]:
                        blueprint_instances_per_main_scene[scene.name].append(nested_blueprint)"""

    for collection in bpy.data.collections: 
        print("collection", collection, collection.name_full, "users", collection.users)

        collection_from_library = False
        for scene in library_scenes: # should be only in library scenes
            collection_from_library = scene.user_of_id(collection) > 0
            if collection_from_library:
                break
        if not collection_from_library: 
            continue

        
        if (
            'AutoExport' in collection and collection['AutoExport'] == True # get marked collections
            or export_marked_assets and collection.asset_data is not None # or if you have marked collections as assets you can auto export them too
            or collection.name in list(internal_collection_instances.keys()) # or if the collection has an instance in one of the main scenes
            ):
            blueprint = Blueprint(collection.name)
            blueprint.local = True
            blueprint.objects = [object.name for object in collection.all_objects if not object.instance_type == 'COLLECTION'] # inneficient, double loop
            blueprint.nested_blueprints = [object.instance_collection.name for object in collection.all_objects if object.instance_type == 'COLLECTION'] # FIXME: not precise enough, aka "what is a blueprint"
            blueprint.collection = collection
            blueprint.instances = internal_collection_instances[collection.name] if collection.name in internal_collection_instances else []

            blueprints[collection.name] = blueprint

            # now create reverse lookup , so you can find the collection from any of its contained objects
            for object in collection.all_objects:
                blueprints_from_objects[object.name] = collection.name

        #
        collections.append(collection)

    # add any collection that has an instance in the main scenes, but is not present in any of the scenes (IE NON LOCAL)
    for collection_name in external_collection_instances:
        collection = bpy.data.collections[collection_name]
        blueprint = Blueprint(collection.name)
        blueprint.local = False
        blueprint.objects = [object.name for object in collection.all_objects if not object.instance_type == 'COLLECTION'] # inneficient, double loop
        blueprint.nested_blueprints = [object.instance_collection.name for object in collection.all_objects if object.instance_type == 'COLLECTION'] # FIXME: not precise enough, aka "what is a blueprint"
        blueprint.collection = collection
        blueprint.instances = external_collection_instances[collection.name] if collection.name in external_collection_instances else []

        blueprints[collection.name] = blueprint

        # now create reverse lookup , so you can find the collection from any of its contained objects
        for object in collection.all_objects:
            blueprints_from_objects[object.name] = collection.name


    # then add any nested collections at root level
    for blueprint_name in list(blueprints.keys()):
        parent_blueprint = blueprints[blueprint_name]
        for nested_blueprint_name in parent_blueprint.nested_blueprints:
            if not nested_blueprint_name in blueprints.keys():
                collection = bpy.data.collections[nested_blueprint_name]
                blueprint = Blueprint(collection.name)
                blueprint.local = parent_blueprint.local
                blueprint.objects = [object.name for object in collection.all_objects if not object.instance_type == 'COLLECTION'] # inneficient, double loop
                blueprint.nested_blueprints = [object.instance_collection.name for object in collection.all_objects if object.instance_type == 'COLLECTION'] # FIXME: not precise enough, aka "what is a blueprint"
                blueprint.collection = collection
                blueprint.instances = external_collection_instances[collection.name] if collection.name in external_collection_instances else []

                blueprints[collection.name] = blueprint


    blueprints = dict(sorted(blueprints.items()))

    print("BLUEPRINTS")
    for blueprint_name in blueprints:
        print(" ", blueprints[blueprint_name])

    print("BLUEPRINTS LOOKUP")
    print(blueprints_from_objects)

    print("BLUEPRINT INSTANCES PER MAIN SCENE")
    print(blueprint_instances_per_main_scene)




    changes_test = {'Library': {
        'Blueprint1_mesh': bpy.data.objects['Blueprint1_mesh'], 
        'Fox_mesh': bpy.data.objects['Fox_mesh'],
        'External_blueprint2_Cylinder': bpy.data.objects['External_blueprint2_Cylinder']}
    }
    # which main scene has been impacted by this
    # does one of the main scenes contain an INSTANCE of an impacted blueprint
    for scene in main_scenes:
        changed_objects = list(changes_test["Library"].keys()) # just a hack for testing
        #bluprint_instances_in_scene = blueprint_instances_per_main_scene[scene.name]
        #print("instances per scene", bluprint_instances_in_scene, "changed_objects", changed_objects)

        changed_blueprints_with_instances_in_scene = [blueprints_from_objects[changed] for changed in changed_objects if changed in blueprints_from_objects]
        print("changed_blueprints_with_instances_in_scene", changed_blueprints_with_instances_in_scene)
        level_needs_export = len(changed_blueprints_with_instances_in_scene) > 0
        if level_needs_export:
            print("level needs export", scene.name)

    for scene in library_scenes:
        changed_objects = list(changes_test[scene.name].keys())
        changed_blueprints = [blueprints_from_objects[changed] for changed in changed_objects if changed in blueprints_from_objects]
        # we only care about local blueprints/collections
        changed_local_blueprints = [blueprint_name for blueprint_name in changed_blueprints if blueprint_name in blueprints.keys() and blueprints[blueprint_name].local]
        print("changed blueprints", changed_local_blueprints)
        
