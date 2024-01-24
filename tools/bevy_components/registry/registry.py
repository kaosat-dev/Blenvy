import bpy
import json
import os
from pathlib import Path
from bpy_types import (PropertyGroup)
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty, CollectionProperty)

# helper class to store missing bevy types information
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

        "u8": dict(type=IntProperty, presets=dict(min=0, max=255)),
        "u16": dict(type=IntProperty, presets=dict(min=0, max=65535)),
        "u32": dict(type=IntProperty, presets=dict(min=0)),
        "u64": dict(type=IntProperty, presets=dict(min=0)),
        "u128": dict(type=IntProperty, presets=dict(min=0)),
        "u64": dict(type=IntProperty, presets=dict(min=0)),
        "usize": dict(type=IntProperty, presets=dict(min=0)),

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
        "glam::UVec4":{"type": FloatVectorProperty, "presets": {"size":4, "min":0.0} },

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
                #delattr(bpy.types.Object, propgroup_name)
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


"""
    object[component_definition.name] = 0.5
    property_manager = object.id_properties_ui(component_definition.name)
    property_manager.update(min=-10, max=10, soft_min=-5, soft_max=5)

    print("property_manager", property_manager)

    object[component_definition.name] = [0.8,0.2,1.0]
    property_manager = object.id_properties_ui(component_definition.name)
    property_manager.update(subtype='COLOR')

    #IDPropertyUIManager
    #rna_ui = object[component_definition.name].get('_RNA_UI')
"""