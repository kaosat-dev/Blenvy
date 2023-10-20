bl_info = {
    "name": "gltf_auto_export",
    "author": "kaosigh",
    "version": (0, 5),
    "blender": (3, 4, 0),
    "location": "File > Import-Export",
    "description": "glTF/glb auto-export",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import os
import bpy
import traceback
from bpy.types import Operator, AddonPreferences
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ExportHelper
from bpy.props import (BoolProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

bpy.context.window_manager['changed_objects_per_scene'] = {}
bpy.context.window_manager['previous_params'] = {}
bpy.context.window_manager['__gltf_auto_export_initialized'] = False
bpy.context.window_manager['__gltf_auto_export_gltf_params_changed'] = False

scene_key = "auto_gltfExportSettings"


################## 
### internals too

class SceneLink(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="")
    scene: bpy.props.PointerProperty(type=bpy.types.Scene)

class SceneLinks(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="List of scenes to export", default="Unknown")
    items: bpy.props.CollectionProperty(type = SceneLink)

class CUSTOM_PG_sceneName(bpy.types.PropertyGroup):
    # name: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    display: bpy.props.BoolProperty()
    # scene:bpy.props.PointerProperty(type=bpy.types.Scene, name="library scene", description="foo")


################
# TODO: move this out
class CUSTOM_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "scene_list.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))
    

    scene_type: bpy.props.StringProperty()#TODO: replace with enum

    def invoke(self, context, event):
        print("INVOKE", self.scene_type, __name__)
        source = bpy.context.preferences.addons[__name__].preferences
        target_name = "library_scenes"
        target_index = "library_scenes_index"
        if self.scene_type == "level":
            target_name = "main_scenes"
            target_index = "main_scenes_index"
        
        target = getattr(source, target_name)
        idx = getattr(source, target_index)

        try:
            item = target[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(target) - 1:
                item_next = target[idx + 1].name
                target.move(idx, idx + 1)
                source[target_index] += 1
                info = 'Item "%s" moved to position %d' % (item.name, source[target_index] + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = target[idx - 1].name
                target.move(idx, idx - 1)
                source[target_index] -= 1
                info = 'Item "%s" moved to position %d' % (item.name, source[target_index] + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (target[idx].name)
                source[target_index] -= 1
                target.remove(idx)
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            item = target.add()
            item.name = f"Rule {idx +1}"
            #name = f"Rule {idx +1}"
            #target.append({"name": name})

            source[target_index] = len(target) - 1
            info = '"%s" added to list' % (item.name)
            self.report({'INFO'}, info)
        
        return {"FINISHED"}



#############


#see here for original gltf exporter infos https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/addons/io_scene_gltf2/__init__.py
@persistent
def deps_update_handler(scene, depsgraph):
    if scene.name != "temp_scene": # actually do we care about anything else than the main scene(s) ?
        print("depsgraph_update_post", scene.name)
        print("-------------")
        changed = scene.name or ""

        # depsgraph = bpy.context.evaluated_depsgraph_get()
        if not 'changed_objects_per_scene' in bpy.context.window_manager:
            bpy.context.window_manager['changed_objects_per_scene'] = {}

        if not changed in bpy.context.window_manager['changed_objects_per_scene']:
            bpy.context.window_manager['changed_objects_per_scene'][changed] = {}
        
        for obj in depsgraph.updates:
            if isinstance(obj.id, bpy.types.Object):
                # get the actual object
                object = bpy.data.objects[obj.id.name]
                bpy.context.window_manager['changed_objects_per_scene'][scene.name][obj.id.name] = object
        
        bpy.context.window_manager.changedScene = changed

@persistent
def save_handler(dummy): 
    print("-------------")
    print("saved", bpy.data.filepath)
    if not 'changed_objects_per_scene' in bpy.context.window_manager:
        bpy.context.window_manager['changed_objects_per_scene'] = {}
    changes_per_scene =  bpy.context.window_manager['changed_objects_per_scene']

    #determine changed parameters
    addon_prefs = bpy.context.preferences.addons[__name__].preferences

    prefs = {}
    for (k,v) in addon_prefs.items():
        if k not in AutoExportGltfPreferenceNames:
            prefs[k] = v

    set1 = set(bpy.context.window_manager['previous_params'].items())
    set2 = set(prefs.items())
    difference = dict(set1 ^ set2)
    
    changed_param_names = list(set(difference.keys())- set(AutoExportGltfPreferenceNames))
    changed_parameters = len(changed_param_names) > 0
    # do the export
    auto_export(changes_per_scene, changed_parameters)


    # save the parameters
    # todo add back
    for (k, v) in prefs.items():
        bpy.context.window_manager['previous_params'][k] = v

    # reset a few things after exporting
    # reset wether the gltf export paramters were changed since the last save 
    bpy.context.window_manager['__gltf_auto_export_gltf_params_changed'] = False
    # reset whether there have been changed objects since the last save 
    bpy.context.window_manager['changed_objects_per_scene'] = {}

def get_changedScene(self):
    return self["changedScene"]

def set_changedScene(self, value):
    self["changedScene"] = value


#https://docs.blender.org/api/current/bpy.ops.export_scene.html#bpy.ops.export_scene.gltf
def export_gltf (path, export_settings):
    settings = {**export_settings, "filepath": path}
    bpy.ops.export_scene.gltf(**settings)


#####################################################
#### Helpers ####

def get_collection_hierarchy(root_col, levels=1):
    """Read hierarchy of the collections in the scene"""
    level_lookup = {}
    def recurse(root_col, parent, depth):
        if depth > levels: 
            return
        if isinstance(parent,  bpy.types.Collection):
            level_lookup.setdefault(parent, []).append(root_col)
        for child in root_col.children:
            recurse(child, root_col,  depth + 1)
    recurse(root_col, root_col.children, 0)
    return level_lookup

# the active collection is a View Layer concept, so you actually have to find the active LayerCollection
# which must be done recursively
def find_layer_collection_recursive(find, col):
    print("root collection", col)
    for c in col.children:
        print("child collection", c)
        if c.collection == find:
            return c
    return None

#Recursivly transverse layer_collection for a particular name
def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found


# Makes an empty, at location, stores it in existing collection, from https://blender.stackexchange.com/questions/51290/how-to-add-empty-object-not-using-bpy-ops
def make_empty(name, location, coll_name): #string, vector, string of existing coll
    empty_obj = bpy.data.objects.new( "empty", None, )
    empty_obj.name = name
    empty_obj.empty_display_size = 1 
    bpy.data.collections[coll_name].objects.link(empty_obj)
    empty_obj.location = location
    return empty_obj


def make_empty2(name, location, collection):
    object_data = None #bpy.data.meshes.new("NewMesh") #None
    empty_obj = bpy.data.objects.new( name, object_data )
    empty_obj.name = name
    empty_obj.location = location


    empty_obj.empty_display_size = 2
    empty_obj.empty_display_type = 'PLAIN_AXES'   
    collection.objects.link( empty_obj )
    return empty_obj

def make_empty3(name, location, rotation, scale, collection): 
    original_active_object = bpy.context.active_object
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location, rotation=rotation, scale=scale)
    empty_obj = bpy.context.active_object
    empty_obj.name = name
    empty_obj.scale = scale # scale is not set correctly ?????
    bpy.context.view_layer.objects.active = original_active_object
    return empty_obj

# generate a copy of a scene that replaces collection instances with empties
# alternative: copy original names before creating a new scene, & reset them
# or create empties, hide original ones, and do the same renaming trick
def generate_hollow_scene(scene): 
    root_collection = scene.collection 
    temp_scene = bpy.data.scenes.new(name="temp_scene")
    copy_root_collection = temp_scene.collection
    scene_objects = [o for o in root_collection.objects]

    # we set our active scene to be this one : this is needed otherwise the stand-in empties get generated in the wrong scene
    bpy.context.window.scene = temp_scene

    found = find_layer_collection_recursive(copy_root_collection, bpy.context.view_layer.layer_collection)
    if found:
        print("FOUND COLLECTION")
        # once it's found, set the active layer collection to the one we found
        bpy.context.view_layer.active_layer_collection = found
    
    #original_names = {}
    original_names = []
    for object in scene_objects:
        if object.instance_type == 'COLLECTION':
            collection_name = object.instance_collection.name

            #original_names[object.name] = object.name# + "____bak"
            #print("custom properties", object, object.keys(), object.items())
            #for k, e in object.items():
            #    print("custom properties ", k, e)
            print("object location", object.location)
            original_name = object.name
            original_names.append(original_name)

            object.name = original_name + "____bak"
            empty_obj = make_empty3(original_name, object.location, object.rotation_euler, object.scale, copy_root_collection)
            """we inject the collection/blueprint name, as a component called 'BlueprintName', but we only do this in the empty, not the original object"""
            empty_obj['BlueprintName'] = '"'+collection_name+'"'
            empty_obj['SpawnHere'] = ''

            for k, v in object.items():
                empty_obj[k] = v
        else:
            copy_root_collection.objects.link(object)

    # bpy.data.scenes.remove(temp_scene)
    # objs = bpy.data.objects
    #objs.remove(objs["Cube"], do_unlink=True)
    return (temp_scene, original_names)

# clear & remove "hollow scene"
def clear_hollow_scene(temp_scene, original_scene, original_names):
    # reset original names
    root_collection = original_scene.collection 
    scene_objects = [o for o in root_collection.objects]

    for object in scene_objects:
        if object.instance_type == 'COLLECTION':
            if object.name.endswith("____bak"):
                object.name = object.name.replace("____bak", "")

    # remove empties (only needed when we go via ops ????)
    root_collection = temp_scene.collection 
    scene_objects = [o for o in root_collection.objects]
    for object in scene_objects:
        if object.type == 'EMPTY':
            if hasattr(object, "SpawnHere"):
                bpy.data.objects.remove(object, do_unlink=True)
            else: 
                bpy.context.scene.collection.objects.unlink(object)
            #bpy.data.objects.remove(object, do_unlink=True)

    bpy.data.scenes.remove(temp_scene)


# returns the list of the collections in use for a given scene
def get_used_collections(scene): 
    root_collection = scene.collection 

    scene_objects = [o for o in root_collection.objects]
    collection_names = set()
    used_collections = []
    for object in scene_objects:
        #print("object ", object)
        if object.instance_type == 'COLLECTION':
            #print("THIS OBJECT IS A COLLECTION")
            # print("instance_type" ,object.instance_type)
            collection_name = object.instance_collection.name
            #print("instance collection", object.instance_collection.name)
            #object.instance_collection.users_scene
            # del object['blueprint']
            # object['BlueprintName'] = '"'+collection_name+'"'
            if not collection_name in collection_names: 
                collection_names.add(collection_name)
                used_collections.append(object.instance_collection)

    #print("scene objects", scene_objects) 
    return (collection_names, used_collections)


def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

# gets all collections that should ALWAYS be exported to their respective gltf files, even if they are not used in the main scene/level
def get_marked_collections(scene):
    # print("checking library for marked collections")
    root_collection = scene.collection
    marked_collections = []
    collection_names = []
    for collection in traverse_tree(root_collection):
        if 'AutoExport' in collection and collection['AutoExport'] == True:
            marked_collections.append(collection)
            collection_names.append(collection.name)
    return (collection_names, marked_collections)


def generate_gltf_export_preferences(addon_prefs): 
    # default values
    gltf_export_preferences = dict(
        export_format= 'GLB', #'GLB', 'GLTF_SEPARATE', 'GLTF_EMBEDDED'
        check_existing=False,

        use_selection=False,
        use_visible=True, # Export visible and hidden objects. See Object/Batch Export to skip.
        use_renderable=False,
        use_active_collection= False,
        use_active_collection_with_nested=False,
        use_active_scene = False,

        export_texcoords=True,
        export_normals=True,
        # here add draco settings
        export_draco_mesh_compression_enable = False,

        export_tangents=False,
        #export_materials
        export_colors=True,
        export_attributes=True,
        #use_mesh_edges
        #use_mesh_vertices
        export_cameras=True,
        export_extras=True, # For custom exported properties.
        export_lights=True,
        export_yup=True,
        export_skins=True,
        export_morph=False,
        export_apply=False,
        export_animations=False
    )
        
    for key in addon_prefs.__annotations__.keys():
        if str(key) not in AutoExportGltfPreferenceNames:
            #print("overriding setting", key, "value", getattr(addon_prefs,key))
            gltf_export_preferences[key] = getattr(addon_prefs,key)

    return gltf_export_preferences


# get exportable collections from lists of mains scenes and lists of library scenes
def get_exportable_collections(main_scenes, library_scenes): 
    all_collections = []
    for main_scene in main_scenes:
        (collection_names, _) = get_used_collections(main_scene)
        all_collections = all_collections + list(collection_names)
    for library_scene in library_scenes:
        marked_collections = get_marked_collections(library_scene)
        all_collections = all_collections + marked_collections[0]
    return all_collections

def check_if_blueprints_exist(collections, folder_path, extension):
    not_found_blueprints = []
    for collection_name in collections:
        gltf_output_path = os.path.join(folder_path, collection_name + extension)
        print("gltf_output_path", gltf_output_path)
        found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
        if not found:
            not_found_blueprints.append(collection_name)
    return not_found_blueprints

######################################################
#### Export logic #####

# find which of the library scenes the given collection stems from
# TODO: does not seem efficient at all ?
def get_source_scene(collection_name, library_scenes): 
    match = None
    for scene in library_scenes:
        root_collection = scene.collection
        found = False
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name == collection_name:
                found = True
                break
        if found:
            match = scene
            break
    return match

def get_collections_per_scene(collection_names, library_scenes): 
    collections_per_scene = {}
    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                if not scene.name in collections_per_scene:
                    collections_per_scene[scene.name] = []
                collections_per_scene[scene.name].append(cur_collection.name)
                
    return collections_per_scene

# export collections: all the collections that have an instance in the main scene AND any marked collections, even if they do not have instances
def export_collections(collections, folder_path, library_scene, addon_prefs, gltf_export_preferences): 
    # set active scene to be the library scene (hack for now)
    bpy.context.window.scene = library_scene
    # save current active collection
    active_collection =  bpy.context.view_layer.active_layer_collection

    for collection_name in collections:
        print("exporting collection", collection_name)
        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = recurLayerCollection(layer_collection, collection_name)
        # set active collection to the collection
        bpy.context.view_layer.active_layer_collection = layerColl

        gltf_output_path = os.path.join(folder_path, collection_name)

        export_settings = { **gltf_export_preferences, 'use_active_scene': True, 'use_active_collection': True, 'use_active_collection_with_nested':True} #'use_visible': False,
        export_gltf(gltf_output_path, export_settings)
    
    # reset active collection to the one we save before
    bpy.context.view_layer.active_layer_collection = active_collection


def export_blueprints_from_collections(collections, library_scene, folder_path, addon_prefs):
    export_output_folder = getattr(addon_prefs,"export_output_folder")
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    export_blueprints_path = os.path.join(folder_path, export_output_folder, getattr(addon_prefs,"export_blueprints_path")) if getattr(addon_prefs,"export_blueprints_path") != '' else folder_path

    #print("-----EXPORTING BLUEPRINTS----")
    #print("LIBRARY EXPORT", export_blueprints_path )

    try:
        export_collections(collections, export_blueprints_path, library_scene, addon_prefs, gltf_export_preferences)
    except Exception as error:
        print("failed to export collections to gltf: ", error)
        # TODO : rethrow


# export all main scenes
def export_main_scenes(scenes, folder_path, addon_prefs): 
    for scene in scenes:
        export_main_scene(scene, folder_path, addon_prefs)

def export_main_scene(scene, folder_path, addon_prefs): 
    export_output_folder = getattr(addon_prefs,"export_output_folder")
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    print("exporting to", folder_path, export_output_folder)

    export_blueprints = getattr(addon_prefs,"export_blueprints")
  
    if export_blueprints : 
        (hollow_scene, object_names) = generate_hollow_scene(scene)
        #except Exception:
        #    print("failed to create hollow scene")

        # set active scene to be the given scene
        bpy.context.window.scene = hollow_scene

    gltf_output_path = os.path.join(folder_path, export_output_folder, scene.name)

    export_settings = { **gltf_export_preferences, 
                       'use_active_scene': True, 
                       'use_active_collection':True, 
                       'use_active_collection_with_nested':True,  
                       'use_visible': False,
                       'use_renderable': False,
                       'export_apply':True
                       }
    export_gltf(gltf_output_path, export_settings)

    if export_blueprints : 
        clear_hollow_scene(hollow_scene, scene, object_names)

"""Main function"""
def auto_export(changes_per_scene, changed_export_parameters):
    addon_prefs = bpy.context.preferences.addons[__name__].preferences

    # a semi_hack to ensure we have the latest version of the settings
    initialized = bpy.context.window_manager['__gltf_auto_export_initialized'] if '__gltf_auto_export_initialized' in bpy.context.window_manager else False
    if not initialized:
        print("not initialized, fetching settings if any")
        # semi_hack to restore the correct settings if the add_on was installed before
        settings = bpy.context.scene.get(scene_key)
        if settings:
            print("loading settings")
            try:
                # Update filter if user saved settings
                #if hasattr(self, 'export_format'):
                #    self.filter_glob = '*.glb' if self.export_format == 'GLB' else '*.gltf'
                for (k, v) in settings.items():
                    setattr(addon_prefs, k, v)
            except Exception as error:
                print("error setting preferences from saved settings", error)
        bpy.context.window_manager['__gltf_auto_export_initialized'] = True

    # have the export parameters (not auto export, just gltf export) have changed: if yes (for example switch from glb to gltf, compression or not, animations or not etc), we need to re-export everything
    print ("changed_export_parameters", changed_export_parameters)
    try:
        file_path = bpy.data.filepath
        # Get the folder
        folder_path = os.path.dirname(file_path)
        # get the preferences for our addon

        export_blueprints = getattr(addon_prefs,"export_blueprints")
        export_output_folder = getattr(addon_prefs,"export_output_folder")

        main_scene_names= list(map(lambda scene: scene.name, getattr(addon_prefs,"main_scenes")))
        library_scene_names = list(map(lambda scene: scene.name, getattr(addon_prefs,"library_scenes")))
        print("main scenes", main_scene_names, "library_scenes", library_scene_names)
        print("export_output_folder", export_output_folder)

        # export the main game world
        level_scenes = list(map(lambda name: bpy.data.scenes[name], main_scene_names))
        library_scenes = list(map(lambda name: bpy.data.scenes[name], library_scene_names))

        # export everything everytime
        if export_blueprints:
            print("EXPORTING")
            # get a list of all collections actually in use
            collections = get_exportable_collections(level_scenes, library_scenes)
            # first check if all collections have already been exported before (if this is the first time the exporter is run
            # in your current Blender session for example)
            export_blueprints_path = os.path.join(folder_path, export_output_folder, getattr(addon_prefs,"export_blueprints_path")) if getattr(addon_prefs,"export_blueprints_path") != '' else folder_path

            gltf_extension = getattr(addon_prefs, "export_format")
            gltf_extension = '.glb' if gltf_extension == 'GLB' else '.gltf'
            collections_not_on_disk = check_if_blueprints_exist(collections, export_blueprints_path, gltf_extension)
            changed_collections = []

            print('changes_per_scene', changes_per_scene.items(), changes_per_scene.keys())
            for scene, bla in changes_per_scene.items():
                print("  changed scene", scene)
                for obj_name, obj in bla.items():
                    object_collections = list(obj.users_collection)
                    object_collection_names = list(map(lambda collection: collection.name, object_collections))
                    if len(object_collection_names) > 1:
                        print("ERRROR, objects in multiple collections not supported")
                    else:
                        object_collection_name =  object_collection_names[0] if len(object_collection_names) > 0 else None
                        print("      object ", obj, object_collection_name)
                        if object_collection_name in collections:
                            changed_collections.append(object_collection_name)

            collections_to_export = list(set(changed_collections + collections_not_on_disk))

            # we need to re_export everything if the export parameters have been changed
            collections_to_export = collections if changed_export_parameters else collections_to_export
            collections_per_scene = get_collections_per_scene(collections_to_export, library_scenes)

            print("--------------")
            print("collections:               all:", collections)
            print("collections:           changed:", changed_collections)
            print("collections: not found on disk:", collections_not_on_disk)
            print("collections:          to export:", collections_to_export)
            print("collections:          per_scene:", collections_per_scene)

            # backup current active scene
            old_current_scene = bpy.context.scene
            # backup current selections
            old_selections = bpy.context.selected_objects

            # first export any main/level/world scenes
            print("export MAIN scenes")
            for scene_name in main_scene_names:
                do_export_main_scene =  changed_export_parameters or (scene_name in changes_per_scene.keys() and len(changes_per_scene[scene_name].keys()) > 0) 
                if do_export_main_scene:
                    print("     exporting scene:", scene_name)
                    export_main_scene(bpy.data.scenes[scene_name], folder_path, addon_prefs)


            # now deal with blueprints/collections
            do_export_library_scene = changed_export_parameters or len(collections_to_export) > 0 # export_library_scene_name in changes_per_scene.keys()
            print("export LIBRARY")
            if do_export_library_scene:
                # we only want to go through the library scenes where our collections to export are present
                for (scene_name, collections_to_export)  in collections_per_scene.items():
                    print("     exporting collections from scene:", scene_name)
                    print("     collections to export", collections_to_export)
                    library_scene = bpy.data.scenes[scene_name]
                    export_blueprints_from_collections(collections_to_export, library_scene, folder_path, addon_prefs)


            # reset current scene from backup
            bpy.context.window.scene = old_current_scene
            # reset selections
            for obj in old_selections:
                obj.select_set(True)


        else:
            print("dsfsfsdf")
            for scene_name in main_scene_names:
                export_main_scene(bpy.data.scenes[scene_name], folder_path, addon_prefs)

    except Exception as error:
        traceback.print_stack()
        def error_message(self, context):
            self.layout.label(text="Failure during auto_export: please check your main scene name & make sure your output folder exists. Error: "+ str(error))

        bpy.context.window_manager.popup_menu(error_message, title="Error", icon='ERROR')




######################################################
## ui logic & co

AutoExportGltfPreferenceNames = [
    'auto_export',
    'export_main_scene_name',
    'export_output_folder',
    'export_library_scene_name',
    'export_blueprints',
    'export_blueprints_path',

    'main_scenes',
    'library_scenes'
]

class AutoExportGltfAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__
    bl_options = {'PRESET'}

    auto_export: BoolProperty(
        name='Auto export',
        description='Automatically export to gltf on save',
        default=True
    )
    export_main_scene_name: StringProperty(
        name='Main scene',
        description='The name of the main scene/level/world to auto export',
        default='Scene'
    )
    export_output_folder: StringProperty(
        name='Export folder (relative)',
        description='The root folder for all exports(relative to current file) Defaults to current folder',
        default=''
    )
    export_library_scene_name: StringProperty(
        name='Library scene',
        description='The name of the library scene to auto export',
        default='Library'
    )
    # blueprint settings
    export_blueprints: BoolProperty(
        name='Export Blueprints',
        description='Replaces collection instances with an Empty with a BlueprintName custom property',
        default=True
    )
    export_blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to the Export folder)',
        default='library'
    )

    main_scenes: CollectionProperty(name="main scenes", type=CUSTOM_PG_sceneName)
    main_scenes_index: IntProperty(name = "Index for main scenes list", default = 0)

    library_scenes: CollectionProperty(name="library scenes", type=CUSTOM_PG_sceneName)
    library_scenes_index: IntProperty(name = "Index for library scenes list", default = 0)

    #####
    export_format: EnumProperty(
        name='Format',
        items=(('GLB', 'glTF Binary (.glb)',
                'Exports a single file, with all data packed in binary form. '
                'Most efficient and portable, but more difficult to edit later'),
               ('GLTF_EMBEDDED', 'glTF Embedded (.gltf)',
                'Exports a single file, with all data packed in JSON. '
                'Less efficient than binary, but easier to edit later'),
               ('GLTF_SEPARATE', 'glTF Separate (.gltf + .bin + textures)',
                'Exports multiple files, with separate JSON, binary and texture data. '
                'Easiest to edit later')),
        description=(
            'Output format and embedding options. Binary is most efficient, '
            'but JSON (embedded or separate) may be easier to edit later'
        ),
        default='GLB'
    )
    export_copyright: StringProperty(
        name='Copyright',
        description='Legal rights and conditions for the model',
        default=''
    )

    export_image_format: EnumProperty(
        name='Images',
        items=(('AUTO', 'Automatic',
                'Save PNGs as PNGs and JPEGs as JPEGs. '
                'If neither one, use PNG'),
                ('JPEG', 'JPEG Format (.jpg)',
                'Save images as JPEGs. (Images that need alpha are saved as PNGs though.) '
                'Be aware of a possible loss in quality'),
                ('NONE', 'None',
                 'Don\'t export images'),
               ),
        description=(
            'Output format for images. PNG is lossless and generally preferred, but JPEG might be preferable for web '
            'applications due to the smaller file size. Alternatively they can be omitted if they are not needed'
        ),
        default='AUTO'
    )

    export_texture_dir: StringProperty(
        name='Textures',
        description='Folder to place texture files in. Relative to the .gltf file',
        default='',
    )

    """
    export_jpeg_quality: IntProperty(
        name='JPEG quality',
        description='Quality of JPEG export',
        default=75,
        min=0,
        max=100
    )
    """

    export_keep_originals: BoolProperty(
        name='Keep original',
        description=('Keep original textures files if possible. '
                     'WARNING: if you use more than one texture, '
                     'where pbr standard requires only one, only one texture will be used. '
                     'This can lead to unexpected results'
        ),
        default=False,
    )

    export_texcoords: BoolProperty(
        name='UVs',
        description='Export UVs (texture coordinates) with meshes',
        default=True
    )

    export_normals: BoolProperty(
        name='Normals',
        description='Export vertex normals with meshes',
        default=True
    )

    export_draco_mesh_compression_enable: BoolProperty(
        name='Draco mesh compression',
        description='Compress mesh using Draco',
        default=False
    )

    export_draco_mesh_compression_level: IntProperty(
        name='Compression level',
        description='Compression level (0 = most speed, 6 = most compression, higher values currently not supported)',
        default=6,
        min=0,
        max=10
    )

    export_draco_position_quantization: IntProperty(
        name='Position quantization bits',
        description='Quantization bits for position values (0 = no quantization)',
        default=14,
        min=0,
        max=30
    )

    export_draco_normal_quantization: IntProperty(
        name='Normal quantization bits',
        description='Quantization bits for normal values (0 = no quantization)',
        default=10,
        min=0,
        max=30
    )

    export_draco_texcoord_quantization: IntProperty(
        name='Texcoord quantization bits',
        description='Quantization bits for texture coordinate values (0 = no quantization)',
        default=12,
        min=0,
        max=30
    )

    export_draco_color_quantization: IntProperty(
        name='Color quantization bits',
        description='Quantization bits for color values (0 = no quantization)',
        default=10,
        min=0,
        max=30
    )

    export_draco_generic_quantization: IntProperty(
        name='Generic quantization bits',
        description='Quantization bits for generic coordinate values like weights or joints (0 = no quantization)',
        default=12,
        min=0,
        max=30
    )

    export_tangents: BoolProperty(
        name='Tangents',
        description='Export vertex tangents with meshes',
        default=False
    )

    export_materials: EnumProperty(
        name='Materials',
        items=(('EXPORT', 'Export',
        'Export all materials used by included objects'),
        ('PLACEHOLDER', 'Placeholder',
        'Do not export materials, but write multiple primitive groups per mesh, keeping material slot information'),
        ('NONE', 'No export',
        'Do not export materials, and combine mesh primitive groups, losing material slot information')),
        description='Export materials',
        default='EXPORT'
    )

    export_original_specular: BoolProperty(
        name='Export original PBR Specular',
        description=(
            'Export original glTF PBR Specular, instead of Blender Principled Shader Specular'
        ),
        default=False,
    )

    export_colors: BoolProperty(
        name='Vertex Colors',
        description='Export vertex colors with meshes',
        default=True
    )

    export_attributes: BoolProperty(
        name='Attributes',
        description='Export Attributes (when starting with underscore)',
        default=False
    )

    use_mesh_edges: BoolProperty(
        name='Loose Edges',
        description=(
            'Export loose edges as lines, using the material from the first material slot'
        ),
        default=False,
    )

    use_mesh_vertices: BoolProperty(
        name='Loose Points',
        description=(
            'Export loose points as glTF points, using the material from the first material slot'
        ),
        default=False,
    )

    export_cameras: BoolProperty(
        name='Cameras',
        description='Export cameras',
        default=True
    )

    use_selection: BoolProperty(
        name='Selected Objects',
        description='Export selected objects only',
        default=False
    )

    use_visible: BoolProperty(
        name='Visible Objects',
        description='Export visible objects only',
        default=True
    )

    use_renderable: BoolProperty(
        name='Renderable Objects',
        description='Export renderable objects only',
        default=False
    )


    export_apply: BoolProperty(
        name='Export Apply Modifiers',
        description='Apply modifiers (excluding Armatures) to mesh objects -'
                    'WARNING: prevents exporting shape keys',
        default=True
    )

    export_yup: BoolProperty(
        name='+Y Up',
        description='Export using glTF convention, +Y up',
        default=True
    )

    use_visible: BoolProperty(
        name='Visible Objects',
        description='Export visible objects only',
        default=False
    )

    use_renderable: BoolProperty(
        name='Renderable Objects',
        description='Export renderable objects only',
        default=False
    )

    export_extras: BoolProperty(
        name='Custom Properties',
        description='Export custom properties as glTF extras',
        default=True
    )

    export_animations: BoolProperty(
        name='Animations',
        description='Exports active actions and NLA tracks as glTF animations',
        default=False
    )

class AutoExportGLTF(Operator, AutoExportGltfAddonPreferences, ExportHelper):
    """test"""
    bl_idname = "export_scenes.auto_gltf"
    bl_label = "Apply settings"
    bl_options = {'PRESET', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ''

    filter_glob: StringProperty(
            default='*.glb;*.gltf', 
            options={'HIDDEN'}
    )

    will_save_settings: BoolProperty(
        name='Remember Export Settings',
        description='Store glTF export settings in the Blender project',
        default=True
    )

    # Custom scene property for saving settings
    scene_key = "auto_gltfExportSettings"

    def save_settings(self, context):
        # find all props to save
        exceptional = [
            # options that don't start with 'export_'  
        ]
        all_props = self.properties
        export_props = {
            x: getattr(self, x) for x in dir(all_props)
            if (x.startswith("export_") or x in exceptional) and all_props.get(x) is not None
        }
        print("saving settings", export_props)#, self.properties, dir(self.properties))
        context.scene[self.scene_key] = export_props

      
    def apply_settings_to_preferences(self, context):
        # find all props to save
        exceptional = [
            # options that don't start with 'export_'  
        ]
        all_props = self.properties
        export_props = {
            x: getattr(self, x) for x in dir(all_props)
            if (x.startswith("export_") or x in exceptional) and all_props.get(x) is not None
        }
        addon_prefs = bpy.context.preferences.addons[__name__].preferences

        for (k, v) in export_props.items():
            setattr(addon_prefs, k, v)


    def execute(self, context):     
        if self.will_save_settings:
            self.save_settings(context)
        # apply the operator properties to the addon preferences
        self.apply_settings_to_preferences(context)

        main_scene_name = context.scene.main_scene.name if context.scene.main_scene else ""
        library_scene_name = context.scene.library_scene.name if context.scene.library_scene else ""
        print("pointers", main_scene_name, "lib", library_scene_name)

        return {'FINISHED'}    
    
    def invoke(self, context, event):
        settings = context.scene.get(self.scene_key)
        self.will_save_settings = False
        if settings:
            print("loading settings")
            try:
                for (k, v) in settings.items():
                    print("loading setting", k, v)
                    setattr(self, k, v)
                self.will_save_settings = True

                # Update filter if user saved settings
                if hasattr(self, 'export_format'):
                    self.filter_glob = '*.glb' if self.export_format == 'GLB' else '*.gltf'

            except (AttributeError, TypeError):
                self.report({"ERROR"}, "Loading export settings failed. Removed corrupted settings")
                del context.scene[self.scene_key]


        addon_prefs = bpy.context.preferences.addons[__name__].preferences

        main_scene_names= list(map(lambda scene: scene.name, getattr(addon_prefs,"main_scenes")))
        library_scene_names = list(map(lambda scene: scene.name, getattr(addon_prefs,"library_scenes")))
        level_scenes = list(map(lambda name: bpy.data.scenes[name], main_scene_names))
        library_scenes = list(map(lambda name: bpy.data.scenes[name], library_scene_names))
       
        collections = get_exportable_collections(level_scenes, library_scenes)

        try:
            # we save this list of collections in the context
            bpy.context.window_manager.exportedCollections.clear()
            #TODO: add error handling for this
            for collection_name in collections:
                ui_info = bpy.context.window_manager.exportedCollections.add()
                ui_info.name = collection_name
        except Exception as error:
            self.report({"ERROR"}, "Failed to populate list of exported collections/blueprints")
     


        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
        # return self.execute(context)

    def draw(self, context):
        pass

class GLTF_PT_auto_export_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = ""
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data


class GLTF_PT_auto_export_root(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Auto export"
    bl_parent_id = "GLTF_PT_auto_export_main"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf"

    def draw_header(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        self.layout.prop(operator, "auto_export", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator
        #operator = bpy.context.preferences.addons[__name__].preferences

        layout.active = operator.auto_export
        layout.prop(operator, 'will_save_settings')
        #layout.prop(operator, "export_main_scene_name")
        #layout.prop(operator, "export_library_scene_name")
        layout.prop(operator, "export_output_folder")


        # scene selectors
        row = layout.row()
        col = row.column(align=True)
        col.prop(context.scene, "main_scene")
        col.separator()
        col = row.column(align=True)
        col.prop(context.scene, "library_scene")

        #layout.prop(context.scene, "FOO")
        source = bpy.context.preferences.addons[__name__].preferences

        rows = 2

        # main/level scenes
        layout.label(text="main scenes")
        row = layout.row()

        row.template_list("SCENES_UL", "level scenes", source, "main_scenes", source, "main_scenes_index", rows=rows)

        col = row.column(align=True)
        add_operator = col.operator("scene_list.list_action", icon='ADD', text="")
        add_operator.action = 'ADD'
        add_operator.scene_type = 'level'

        remove_operator = col.operator("scene_list.list_action", icon='REMOVE', text="")
        remove_operator.action = 'REMOVE'
        remove_operator.scene_type = 'level'
        col.separator()

        #up_operator = col.operator("scene_list.list_action", icon='TRIA_UP', text="")
        #up_operator.action = 'UP'
        #col.operator("scene_list.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        # library scenes
        layout.label(text="library scenes")
        row = layout.row()

        row.template_list("SCENES_UL", "library scenes", source, "library_scenes", source, "library_scenes_index", rows=rows)

        col = row.column(align=True)
        add_operator = col.operator("scene_list.list_action", icon='ADD', text="")
        add_operator.action = 'ADD'
        add_operator.scene_type = 'library'

        remove_operator = col.operator("scene_list.list_action", icon='REMOVE', text="")
        remove_operator.action = 'REMOVE'
        remove_operator.scene_type = 'library'
        col.separator()


      
class GLTF_PT_auto_export_blueprints(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Blueprints"
    bl_parent_id = "GLTF_PT_auto_export_root"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf" #"EXPORT_SCENE_OT_gltf"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator
        # addon_prefs = bpy.context.preferences.addons[__name__].preferences

        layout.prop(operator, "export_blueprints")
        layout.prop(operator, "export_blueprints_path")

class GLTF_PT_auto_export_collections_list(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Blueprints: Exported Collections"
    bl_parent_id = "GLTF_PT_auto_export_blueprints"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf" #"EXPORT_SCENE_OT_gltf"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator
        addon_prefs = bpy.context.preferences.addons[__name__].preferences

        for collection in bpy.context.window_manager.exportedCollections:
            row = layout.row()
            row.label(text=collection.name)

class GLTF_PT_auto_export_gltf(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Gltf"
    bl_parent_id = "GLTF_PT_auto_export_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf" #"EXPORT_SCENE_OT_gltf"
    
    def draw(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences
        layout = self.layout

        sfile = context.space_data
        operator = sfile.active_operator

        #preferences = context.preferences
        #print("ADDON PREFERENCES ", list(preferences.addons.keys()))
        #print("standard blender gltf prefs", list(preferences.addons["io_scene_gltf2"].preferences.keys()))
        # we get the addon preferences from the standard gltf exporter & use those :
        addon_prefs_gltf = preferences.addons["io_scene_gltf2"].preferences

        #addon_prefs = preferences.addons[__name__].preferences

        # print("KEYS", operator.properties.keys())
        #print("BLAS", addon_prefs.__annotations__)
        #print(addon_prefs.__dict__)
        for key in addon_prefs.__annotations__.keys():
            if key not in AutoExportGltfPreferenceNames:
                layout.prop(operator, key)
     

    

class SCENES_UL(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    #   flt_flag is the result of the filtering process for this item.
    #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
    #         need them.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            #if ma:
            #    layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
            #else:
            #    layout.label(text="", translate=False, icon_value=icon)
            layout.prop(item, "name", text="", emboss=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)



def menu_func_import(self, context):
    self.layout.operator(AutoExportGLTF.bl_idname, text="glTF auto Export (.glb/gltf)")

######################################################
# internals
class CollectionToExport(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="")

class CollectionsToExport(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="List of collections to export", default="Unknown")
    items: bpy.props.CollectionProperty(type = CollectionToExport)




######################################################

classes = [
    SceneLink,
    SceneLinks,
    CUSTOM_PG_sceneName,
    SCENES_UL,
    CUSTOM_OT_actions,

    AutoExportGLTF, 
    AutoExportGltfAddonPreferences,

    CollectionToExport,
    CollectionsToExport,

    GLTF_PT_auto_export_main,
    GLTF_PT_auto_export_root,
    GLTF_PT_auto_export_blueprints,
    GLTF_PT_auto_export_collections_list,
    GLTF_PT_auto_export_gltf
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


    bpy.types.Scene.main_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="main scene", description="foo")
    bpy.types.Scene.library_scene = bpy.props.PointerProperty(type=bpy.types.Scene, name="library scene", description="foo")
    
    bpy.types.Scene.scenes_test = bpy.props.CollectionProperty(type=SceneLinks, name="all scenes", description="foo")


    # setup handlers for updates & saving
    bpy.app.handlers.depsgraph_update_post.append(deps_update_handler)
    bpy.app.handlers.save_post.append(save_handler)

    bpy.types.WindowManager.changedScene = bpy.props.StringProperty(get=get_changedScene, set=set_changedScene)
    bpy.types.WindowManager.exportedCollections = bpy.props.CollectionProperty(type=CollectionsToExport)

    # add our addon to the toolbar
    bpy.types.TOPBAR_MT_file_export.append(menu_func_import)



    ## just experiments
    bpy.types.Scene.main_scenes_list_index = IntProperty(name = "Index for main scenes list", default = 0)
    bpy.types.Scene.library_scenes_list_index = IntProperty(name = "Index for library scenes list", default = 0)

    
    mock_main_scenes = ["World", "level2"]
    main_scenes = bpy.context.preferences.addons[__name__].preferences.main_scenes
    for item_name in mock_main_scenes:
        item = main_scenes.add()
        item.name = item_name
    
    mock_library_scenes = ["Library", "Library2"]
    library_scenes = bpy.context.preferences.addons[__name__].preferences.library_scenes
    for item_name in mock_library_scenes:
        item = library_scenes.add()
        item.name = item_name

    bpy.context.preferences.addons[__name__].preferences.main_scenes_index = 0
    bpy.context.preferences.addons[__name__].preferences.library_scenes_index = 0




def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)

    # remove handlers & co
    bpy.app.handlers.depsgraph_update_post.remove(deps_update_handler)
    bpy.app.handlers.save_post.remove(save_handler)
    
    del bpy.types.WindowManager.changedScene
    del bpy.types.WindowManager.exportedCollections

    del bpy.types.Scene.scenes_test

    del bpy.types.Scene.main_scene
    del bpy.types.Scene.library_scene

    del bpy.types.Scene.main_scenes_list_index
    del bpy.types.Scene.library_scenes_list_index



if __name__ == "__main__":
    register()