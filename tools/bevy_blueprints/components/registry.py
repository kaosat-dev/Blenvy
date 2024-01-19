import bpy
import json
import os
from pathlib import Path

from bpy_types import (PropertyGroup)
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty)

# this is where we store the information for all available components
class ComponentsRegistry(PropertyGroup):
    schemaPath: bpy.props.StringProperty(
        name="schema path",
        description="path to the schema file"
    )

    registry: bpy.props. StringProperty(
        name="registry",
        description="component registry"
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
        "glam::Vec3": {"type": FloatVectorProperty, "presets": {"size":3} },
        "glam::Vec3A":{"type": FloatVectorProperty, "presets": {"size":3} },

        "bevy_render::color::Color": dict(type = FloatVectorProperty, presets=dict(subtype='COLOR', size=4)),

        "char": dict(type=StringProperty, presets=dict()),
        "str":  dict(type=StringProperty, presets=dict()),
        "alloc::string::String":  dict(type=StringProperty, presets=dict()),
        "enum":  dict(type=EnumProperty, presets=dict()), 
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
        "glam::Vec3": [0.0, 0.0, 0.0],
        "glam::Vec3A":[0.0, 0.0, 0.0],
        "glam::Vec4": [0.0, 0.0, 0.0, 0.0], 
        "bevy_render::color::Color": [1.0, 1.0, 0.0, 1.0]
    }

    type_infos = None
    component_uis = {}
    short_names_to_long_names = {}

    def load_schema(self):
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

    def __init__(self) -> None:
        super().__init__()
        print("init registry")


