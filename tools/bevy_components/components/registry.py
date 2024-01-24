import bpy
import json
import os
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from bpy_types import (Operator, PropertyGroup, UIList)
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty, CollectionProperty)

from .metadata import add_metadata_to_components_without_metadata, ensure_metadata_for_all_objects, ensure_prop_groups_for_all_objects

from .operators import GenerateComponent_From_custom_property_Operator

from .ui import generate_propertyGroups_for_components

class MissingBevyType(bpy.types.PropertyGroup):
    type_name: bpy.props.StringProperty(
        name="type",
       
    )

# this is where we store the information for all available components
class ComponentsRegistry(PropertyGroup):
    schemaPath: bpy.props.StringProperty(
        name="schema path",
        description="path to the schema file",
        default="../schema.json"
    )
  
    registry: bpy.props. StringProperty(
        name="registry",
        description="component registry"
    )

    missing_type_infos: StringProperty(
        name="missing type infos",
        description="unregistered/missing type infos"
    )

    missing_types_list: CollectionProperty(name="main scenes", type=MissingBevyType)
    missing_types_list_index: IntProperty(name = "Index for main scenes list", default = 0)

    blender_property_mapping = {
        "bool": dict(type=BoolProperty, presets=dict()),

        "u8": dict(type=IntProperty, presets=dict()),
        "u16": dict(type=IntProperty, presets=dict()),
        "u32": dict(type=IntProperty, presets=dict()),
        "u64": dict(type=IntProperty, presets=dict()),
        "u128": dict(type=IntProperty, presets=dict()),
        "u64": dict(type=IntProperty, presets=dict()),
        "usize": dict(type=IntProperty, presets=dict()),

        "i8": dict(type=IntProperty, presets=dict()),
        "i16":dict(type=IntProperty, presets=dict()),
        "i32":dict(type=IntProperty, presets=dict()),
        "i64":dict(type=IntProperty, presets=dict()),
        "i128":dict(type=IntProperty, presets=dict()),

        "f32": dict(type=FloatProperty, presets=dict()),
        "f64": dict(type=FloatProperty, presets=dict()),

        "glam::Vec2": {"type": FloatVectorProperty, "presets": dict(size = 2) },
        "glam::DVec2": {"type": FloatVectorProperty, "presets": dict(size = 2) },
        "glam::UVec2": {"type": FloatVectorProperty, "presets": dict(size = 2) },

        "glam::Vec3": {"type": FloatVectorProperty, "presets": {"size":3} },
        "glam::Vec3A":{"type": FloatVectorProperty, "presets": {"size":3} },
        "glam::DVec3":{"type": FloatVectorProperty, "presets": {"size":3} },
        "glam::UVec3":{"type": FloatVectorProperty, "presets": {"size":3} },

        "glam::Vec4": {"type": FloatVectorProperty, "presets": {"size":4} },
        "glam::Vec4A": {"type": FloatVectorProperty, "presets": {"size":4} },
        "glam::DVec4": {"type": FloatVectorProperty, "presets": {"size":4} },
        "glam::UVec4":{"type": FloatVectorProperty, "presets": {"size":4} },

        "glam::Quat": {"type": FloatVectorProperty, "presets": {"size":4} },

        "bevy_render::color::Color": dict(type = FloatVectorProperty, presets=dict(subtype='COLOR', size=4)),

        "char": dict(type=StringProperty, presets=dict()),
        "str":  dict(type=StringProperty, presets=dict()),
        "alloc::string::String":  dict(type=StringProperty, presets=dict()),
        "enum":  dict(type=EnumProperty, presets=dict()), 

        #"alloc::vec::Vec<alloc::string::String>": dict(type=CollectionProperty, presets=dict(type=PointerProperty(StringProperty))), #FIXME: we need more generic stuff
    }


    value_types_defaults = {
        "string":" ",
        "boolean": True,
        "float": 0.0,
        "uint": 0,
        "int":0,

        # todo : we are re-doing the work of the bevy /rust side here, but it seems more pratical to alway look for the same field name on the blender side for matches
        "bool": True,

        "u8": 0,
        "u16":0,
        "u32":0,
        "u64":0,
        "u128":0,

        "i8": 0,
        "i16":0,
        "i32":0,
        "i64":0,
        "i128":0,

        "f32": 0.0,
        "f64":0.0,

        "char": " ",
        "str": " ",
        "alloc::string::String": " ",

        "glam::Vec2": [0.0, 0.0],
        "glam::DVec2":  [0.0, 0.0],
        "glam::UVec2": [0, 0],

        "glam::Vec3": [0.0, 0.0, 0.0],
        "glam::Vec3A":[0.0, 0.0, 0.0],
        "glam::UVec3": [0, 0, 0],

        "glam::Vec4": [0.0, 0.0, 0.0, 0.0], 
        "glam::DVec4": [0.0, 0.0, 0.0, 0.0], 
        "glam::UVec4": [0, 0, 0, 0], 

        "glam::Quat":  [0.0, 0.0, 0.0, 0.0], 

        "bevy_render::color::Color": [1.0, 1.0, 0.0, 1.0],
    }

    type_infos = None
    type_infos_missing = []
    component_propertyGroups = {}
    short_names_to_long_names = {}


    @classmethod
    def register(cls):
        #bpy.types.WindowManager.missing_bevy_type = MissingBevyType
        bpy.types.WindowManager.components_registry = PointerProperty(type=ComponentsRegistry)

    @classmethod
    def unregister(cls):
        print("unregister registry")
        for propgroup_name in cls.component_propertyGroups.keys():
            print("unregister comp name", propgroup_name)
            try:
                delattr(bpy.types.Object, propgroup_name)
                print("removed propgroup")
            except Exception as error:
                print("failed to remove", error, "fom bpy.types.Object")
        
        del bpy.types.WindowManager.components_registry
        

    def load_schema(self):
        # cleanup missing types list
        self.missing_types_list.clear()
        print("bla", self.schemaPath)
        file_path = bpy.data.filepath

        # Get the folder
        folder_path = os.path.dirname(file_path)
        path =  os.path.join(folder_path, self.schemaPath)

        print("path to defs", path)
        f = Path(bpy.path.abspath(path)) # make a path object of abs path
        with open(path) as f: 
            data = json.load(f) 
            defs = data["$defs"]
            self.registry = json.dumps(defs) # FIXME:eeek !

    # we load the json once, so we do not need to do it over & over again
    def load_type_infos(self):
        ComponentsRegistry.type_infos = json.loads(self.registry)

    # we keep a list of component propertyGroup around 
    def register_component_propertyGroup(self, name, propertyGroup):
        self.component_propertyGroups[name] = propertyGroup

    #for practicality, we add an entry for a reverse lookup (short => long name, since we already have long_name => short_name with the keys of the raw registry)
    def add_shortName_to_longName(self, short_name, long_name):
        self.short_names_to_long_names[short_name] = long_name

    # to be able to give the user more feedback on any missin/unregistered types in their schema file
    def add_missing_typeInfo(self, type_name):
        if not type_name in self.type_infos_missing:
            self.type_infos_missing.append(type_name)
            setattr(self, "missing_type_infos", str(self.type_infos_missing))
            item = self.missing_types_list.add()
            item.type_name = type_name





# TODO: move to UI
class BEVY_COMPONENTS_PT_Configuration(bpy.types.Panel):
    bl_idname = "BEVY_COMPONENTS_PT_Configuration"
    bl_label = "Configuration"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"
    bl_parent_id = "BEVY_COMPONENTS_PT_MainPanel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_description = "list of missing/unregistered type from the bevy side"

    def draw(self, context):
        layout = self.layout
        registry = bpy.context.window_manager.components_registry 

        row = layout.row()
        col = row.column()
        col.enabled = False
        col.prop(registry, "schemaPath", text="Schema file path")
        col = row.column()
        col.operator(OT_OpenFilebrowser.bl_idname, text="Browse for schema.json")

        layout.separator()
        layout.operator(ReloadRegistryOperator.bl_idname, text="reload registry" , icon="FILE_REFRESH")

        layout.separator()
        row = layout.row()
        op = layout.operator(GenerateComponent_From_custom_property_Operator.bl_idname, text="generate components from custom properties" , icon="LOOP_FORWARDS") # TODO make conditional
        row.enabled = registry.type_infos != None

        layout.separator()
        layout.separator()

# TODO: move to UI
class BEVY_COMPONENTS_PT_MissingTypesPanel(bpy.types.Panel):
    bl_idname = "BEVY_COMPONENTS_PT_MissingTypesPanel"
    bl_label = "Bevy Missing/Unregistered Types"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"
    bl_parent_id = "BEVY_COMPONENTS_PT_MainPanel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_description = "list of missing/unregistered type from the bevy side"

    def draw(self, context):
        layout = self.layout
        registry = bpy.context.window_manager.components_registry 

        layout.label(text="Missing types ")
        
        """for missing in getattr(registry, "type_infos_missing"):
            row = layout.row()
            row.label(text=missing)"""

        layout.template_list("MISSING_TYPES_UL_List", "Missing types list", registry, "missing_types_list", registry, "missing_types_list_index")


class ReloadRegistryOperator(Operator):
    """Reload registry operator"""
    bl_idname = "object.reload_registry"
    bl_label = "Reload Registry"
    bl_options = {"UNDO"}

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    )

    def execute(self, context):
        print("reload registry")
        context.window_manager.components_registry.load_schema()
        generate_propertyGroups_for_components()
        print("")
        print("")
        print("")
        #ensure_metadata_for_all_objects()
        add_metadata_to_components_without_metadata(context.object)

        return {'FINISHED'}
    

class OT_OpenFilebrowser(Operator, ImportHelper): 
    bl_idname = "generic.open_filebrowser" 
    bl_label = "Open the file browser" 

    filter_glob: StringProperty( 
        default='*.json', 
        options={'HIDDEN'} 
    )
    def execute(self, context): 
        """Do something with the selected file(s)."""

        filename, extension = os.path.splitext(self.filepath) 
        print('Selected file:', self.filepath)
        print('File name:', filename)
        print('File extension:', extension)

        file_path = bpy.data.filepath
        # Get the folder
        folder_path = os.path.dirname(file_path)
        print("file_path", file_path)
        print("folder_path", folder_path)

        relative_path = os.path.relpath(self.filepath, folder_path)
        print("rel path", relative_path )
        context.window_manager.components_registry.schemaPath = relative_path
        
        return {'FINISHED'}
    

class MISSING_TYPES_UL_List(UIList): 
    """Missing components UIList.""" 

    use_filter_name_reverse: bpy.props.BoolProperty(
        name="Reverse Name",
        default=False,
        options=set(),
        description="Reverse name filtering",
    )

    use_order_name = bpy.props.BoolProperty(name="Name", default=False, options=set(),
                                            description="Sort groups by their name (case-insensitive)")

    def filter_items__(self, context, data, propname): 
        """Filter and order items in the list.""" 
        # We initialize filtered and ordered as empty lists. Notice that # if all sorting and filtering is disabled, we will return # these empty. 
        filtered = [] 
        ordered = [] 
        items = getattr(data, propname)

        helper_funcs = bpy.types.UI_UL_list


        print("filter, order", items, self, dict(self))
        if self.filter_name:
            print("ssdfs", self.filter_name)
            filtered= helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "type_name", reverse=self.use_filter_name_reverse)

        if not filtered:
            filtered = [self.bitflag_filter_item] * len(items)

        if self.use_order_name:
            ordered = helper_funcs.sort_items_by_name(items, "name")
        

        return filtered, ordered 


    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE' # Make sure your code supports all 3 layout types 
        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            row = layout.row()
            #row.enabled = False
            #row.alert = True
            row.prop(item, "type_name", text="")

        elif self.layout_type in {'GRID'}: 
            print("grid")
            layout.alignment = 'CENTER' 
            row = layout.row()
            row.prop(item, "type_name", text="")
