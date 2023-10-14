bl_info = {
    "name": "gltf_auto_export",
    "author": "kaosigh",
    "version": (0, 3),
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
from bpy.types import Operator, AddonPreferences
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ExportHelper
from bpy.props import (BoolProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )





#see here for original gltf exporter infos https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/addons/io_scene_gltf2/__init__.py
@persistent
def deps_update_handler(scene, depsgraph):
    print("depsgraph_update_post", scene.name)
    print("-------------")
    changed_objects = []
    for obj in depsgraph.updates:
        if isinstance(obj.id, bpy.types.Object):
            print("object changed, amazing", obj.id, obj.id.name)
            changed_objects.append(obj.id.name)
    
    changed = scene.name or ""

    bpy.context.window_manager.changedObjects.clear()
    for obj in changed_objects:
        new_entry = bpy.context.window_manager.changedObjects.add()
        new_entry.name = obj
        #bpy.context.window_manager.changedObjects.add(obj)

    print("changed objects", bpy.context.window_manager.changedObjects)

    bpy.context.window_manager.changedScene = changed

@persistent
def save_handler(dummy): 
    print("-------------")
    print("saved", bpy.data.filepath)
    auto_export()


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
        print("object ", object)
        if object.instance_type == 'COLLECTION':
            print("THIS OBJECT IS A COLLECTION")
            # print("instance_type" ,object.instance_type)
            collection_name = object.instance_collection.name
            print("instance collection", object.instance_collection.name)
            #object.instance_collection.users_scene
            # del object['blueprint']
            # object['BlueprintName'] = '"'+collection_name+'"'
            if not collection_name in collection_names: 
                collection_names.add(collection_name)
                used_collections.append(object.instance_collection)

    print("scene objects", scene_objects) 
    return (collection_names, used_collections)


def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

# gets all collections that should ALWAYS be exported to their respective gltf files, even if they are not used in the main scene/level
def get_marked_collections(scene):
    print("checking library for marked collections")
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
            print("overriding setting", key, "value", getattr(addon_prefs,key))
            gltf_export_preferences[key] = getattr(addon_prefs,key)

    return gltf_export_preferences

######################################################
#### Export logic #####

# export collections: all the collections that have an instance in the main scene AND any marked collections, even if they do not have instances
def export_collections(scene, folder_path, addon_prefs, gltf_export_preferences): 
    (collection_names, used_collections) = get_used_collections(scene)
    library_scene = getattr(addon_prefs, "export_library_scene_name")
    marked_collections = get_marked_collections(bpy.data.scenes[library_scene])
    print("used collection names", collection_names, used_collections)
    print("marked collection names", marked_collections[0])
   
    # set active scene to be the library scene (hack for now)
    bpy.context.window.scene = bpy.data.scenes[library_scene]
    # save current active collection
    active_collection =  bpy.context.view_layer.active_layer_collection

    all_collections = list(collection_names) + marked_collections[0]
    # we save this list of collections in the context
    bpy.context.window_manager.exportedCollections.clear()

    for collection_name in all_collections:
        print("exporting collection", collection_name)

        #TODO: add error handling for this
        ui_info = bpy.context.window_manager.exportedCollections.add()
        ui_info.name = collection_name


        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = recurLayerCollection(layer_collection, collection_name)
        # set active collection to the collection
        bpy.context.view_layer.active_layer_collection = layerColl

        gltf_output_path = os.path.join(folder_path, collection_name)

        export_settings = { **gltf_export_preferences, 'use_active_scene': True, 'use_active_collection': True, 'use_active_collection_with_nested':True} #'use_visible': False,
        export_gltf(gltf_output_path, export_settings)
    
    # reset active collection to the one we save before
    bpy.context.view_layer.active_layer_collection = active_collection


def export_main(scene, folder_path, addon_prefs): 
    output_name = getattr(addon_prefs,"export_main_output_name")
    gltf_export_preferences = generate_gltf_export_preferences(addon_prefs)
    print("exporting to", folder_path, output_name)

    export_blueprints = getattr(addon_prefs,"export_blueprints")
    export_blueprints_path = os.path.join(folder_path, getattr(addon_prefs,"export_blueprints_path")) if getattr(addon_prefs,"export_blueprints_path") != '' else folder_path

    # backup current active scene
    old_current_scene = bpy.context.scene
    # backup current selections
    old_selections = bpy.context.selected_objects


    if export_blueprints : 
        print("-----EXPORTING BLUEPRINTS----")
        print("LIBRARY EXPORT", export_blueprints_path )

        try:
            export_collections(scene, export_blueprints_path, addon_prefs, gltf_export_preferences)
        except Exception as error:
            print("failed to export collections to gltf: ", error)

        (hollow_scene, object_names) = generate_hollow_scene(scene)
        #except Exception:
        #    print("failed to create hollow scene")

        # set active scene to be the given scene
        bpy.context.window.scene = hollow_scene

    gltf_output_path = os.path.join(folder_path, output_name)

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

    # reset current scene from backup
    bpy.context.window.scene = old_current_scene
    # reset selections
    for obj in old_selections:
        obj.select_set(True)


"""Main function"""
def auto_export():
    file_path = bpy.data.filepath
    # Get the folder
    folder_path = os.path.dirname(file_path)
    # get the preferences for our addon
    addon_prefs = bpy.context.preferences.addons[__name__].preferences

    print("last changed", bpy.context.window_manager.changedScene)

    # optimised variation
    last_changed = bpy.context.window_manager.changedScene

    export_main_scene_name = getattr(addon_prefs,"export_main_scene_name")
    export_on_library_changes = getattr(addon_prefs,"export_on_library_changes")
    export_library_scene_name = getattr(addon_prefs,"export_library_scene_name")

    # export the main game world
    game_scene = bpy.data.scenes[export_main_scene_name]

    # most recent change was in the main scene (game world/ level)
    if last_changed == export_main_scene_name:
        print("game world changed, exporting game gltf only")
        export_main(game_scene, folder_path, addon_prefs)

    # if the library has changed, so will likely the game world that uses the library assets
    if last_changed == export_library_scene_name and export_library_scene_name != ""  and export_on_library_changes: 
        print("library changed")
        export_main(game_scene, folder_path, addon_prefs)


######################################################
## ui logic & co

AutoExportGltfPreferenceNames = [
    'auto_export',
    'export_main_scene_name',
    'export_main_output_name',
    'export_on_library_changes',
    'export_library_scene_name',
    'export_blueprints',
    'export_blueprints_path'
]

class AutoExportGltfAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__
   
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
    export_main_output_name: StringProperty(
        name='Glb output name',
        description='The glb output name for the main scene to auto export',
        default='world'
    )
    export_on_library_changes: BoolProperty(
        name='Export on library changes',
        description='Export main scene on library changes',
        default=False
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
        default=False
    )
    export_blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to this Blend file)',
        default=''
    )


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

class AutoExportGLTF(Operator, ExportHelper):
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
    """
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
    export_main_output_name: StringProperty(
        name='Glb output name',
        description='The glb output name for the main scene to auto export',
        default='world'
    )
    export_on_library_changes: BoolProperty(
        name='Export on library changes',
        description='Export main scene on library changes',
        default=False
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
        default=False
    )
    export_blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to this Blend file)',
        default=''
    )"""
    
    def draw(self, context):
        pass

    def execute(self, context):     
        preferences = context.preferences
        return {'FINISHED'}    

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
        #operator = sfile.active_operator
        operator = bpy.context.preferences.addons[__name__].preferences

        layout.active = operator.auto_export
        layout.prop(operator, "export_main_scene_name")
        layout.prop(operator, "export_library_scene_name")

        layout.prop(operator, "export_main_output_name")
        layout.prop(operator, "export_on_library_changes")
       
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
        addon_prefs = bpy.context.preferences.addons[__name__].preferences

        layout.prop(addon_prefs, "export_blueprints")
        layout.prop(addon_prefs, "export_blueprints_path")


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

        #preferences = context.preferences
        #print("ADDON PREFERENCES ", list(preferences.addons.keys()))
        #print("standard blender gltf prefs", list(preferences.addons["io_scene_gltf2"].preferences.keys()))
        # we get the addon preferences from the standard gltf exporter & use those :
        addon_prefs_gltf = preferences.addons["io_scene_gltf2"].preferences

        #addon_prefs = preferences.addons[__name__].preferences

        # print("KEYS", dir(addon_prefs))
        #print("BLAS", addon_prefs.__annotations__)
        #print(addon_prefs.__dict__)
        for key in addon_prefs.__annotations__.keys():
            if key not in AutoExportGltfPreferenceNames:
                layout.prop(addon_prefs, key)
        #for key in addon_prefs_gltf.__annotations__.keys():
        #    layout.prop(addon_prefs_gltf, key)

def menu_func_import(self, context):
    self.layout.operator(AutoExportGLTF.bl_idname, text="glTF auto Export (.glb/gltf)")

######################################################
# internals
class ChangedObject(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="")

class ChangedObjects(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="List of changed objects", default="Unknown")
    items: bpy.props.CollectionProperty(type = ChangedObject)


class CollectionToExport(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="")

class CollectionsToExport(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="List of collections to export", default="Unknown")
    items: bpy.props.CollectionProperty(type = CollectionToExport)


######################################################

classes = [
    AutoExportGLTF, 
    AutoExportGltfAddonPreferences,

    ChangedObject,
    ChangedObjects,

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

    # setup handlers for updates & saving
    bpy.app.handlers.depsgraph_update_post.append(deps_update_handler)
    bpy.app.handlers.save_post.append(save_handler)

    bpy.types.WindowManager.changedScene = bpy.props.StringProperty(get=get_changedScene, set=set_changedScene)
    bpy.types.WindowManager.changedObjects = bpy.props.CollectionProperty(type=ChangedObjects)
    bpy.types.WindowManager.exportedCollections = bpy.props.CollectionProperty(type=CollectionsToExport)

    # add our addon to the toolbar
    bpy.types.TOPBAR_MT_file_export.append(menu_func_import)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)

    # remove handlers & co
    bpy.app.handlers.depsgraph_update_post.remove(deps_update_handler)
    bpy.app.handlers.save_post.remove(save_handler)
    
    del bpy.types.WindowManager.changedScene
    del bpy.types.WindowManager.changedObjects
    del bpy.types.WindowManager.exportedCollections

if __name__ == "__main__":
    register()