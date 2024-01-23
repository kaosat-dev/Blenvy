import bpy
import json
import os
from pathlib import Path

from bpy_types import (PropertyGroup)
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty, CollectionProperty)

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
    component_uis = {}
    short_names_to_long_names = {}


    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_registry = PointerProperty(type=ComponentsRegistry)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.components_registry

    def load_schema(self):
        print("bla", self.schemaPath)
        file_path = bpy.data.filepath
        # Get the folder
        folder_path = os.path.dirname(file_path)
        path =  os.path.join(folder_path, "../schema.json")
        print("path to defs", path)
        f = Path(bpy.path.abspath(path)) # make a path object of abs path
        with open(path) as f: 
            data = json.load(f) 
            defs = data["$defs"]
            self.registry = json.dumps(defs) # FIXME:eeek !

    # we load the json once, so we do not need to do it over & over again
    def load_type_infos(self):
        ComponentsRegistry.type_infos = json.loads(self.registry)

    # we keep a list of component UIs around (although, this is semi redundand)
    def register_component_ui(self, name, ui):
        self.component_uis[name] = ui

    #for practicality, we add an entry for a reverse lookup (short => long name, since we already have long_name => short_name with the keys of the raw registry)
    def add_shortName_to_longName(self, short_name, long_name):
        self.short_names_to_long_names[short_name] = long_name

    # to be able to give the user more feedback on any missin/unregistered types in their schema file
    def add_missing_typeInfo(self, type_name):
        if not type_name in self.type_infos_missing:
            self.type_infos_missing.append(type_name)
            setattr(self, "missing_type_infos", str(self.type_infos_missing))





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
        layout.prop(registry, "schemaPath", text="Path to your Bevy schema.json file")
        



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
        #+getattr(registry, "missing_type_infos"))
        for missing in getattr(registry, "type_infos_missing"):
            row = layout.row()
            row.label(text=missing)
