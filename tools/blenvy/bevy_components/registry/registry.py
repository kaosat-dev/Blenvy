import bpy
import json
import os
import uuid
from pathlib import Path
from bpy_types import (PropertyGroup)
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty, CollectionProperty)

from ...settings import load_settings
from ..propGroups.prop_groups import generate_propertyGroups_for_components
from ..components.metadata import ComponentMetadata, ensure_metadata_for_all_objects

# helper class to store missing bevy types information
class MissingBevyType(bpy.types.PropertyGroup):
    long_name: bpy.props.StringProperty(
        name="type",
    ) # type: ignore

# helper function to deal with timer
def toggle_watcher(self, context):
    #print("toggling watcher", self.watcher_enabled, watch_schema, self, bpy.app.timers)
    if not self.watcher_enabled:
        try:
            bpy.app.timers.unregister(watch_schema)
        except Exception as error:
            pass
    else:
        self.watcher_active = True
        bpy.app.timers.register(watch_schema)

def watch_schema():
    self = bpy.context.window_manager.components_registry
    # print("watching schema file for changes")
    try:
        stamp = os.stat(self.schemaFullPath).st_mtime
        stamp = str(stamp)
        if stamp != self.schemaTimeStamp and self.schemaTimeStamp != "":
            print("FILE CHANGED !!", stamp,  self.schemaTimeStamp)
            # see here for better ways : https://stackoverflow.com/questions/11114492/check-if-a-file-is-not-open-nor-being-used-by-another-process
            """try:
                os.rename(path, path)
                #return False
            except OSError:    # file is in use
                print("in use")
                #return True"""
            #bpy.ops.object.reload_registry()
            # we need to add an additional delay as the file might not have loaded yet
            bpy.app.timers.register(lambda: bpy.ops.object.reload_registry(), first_interval=1)

        self.schemaTimeStamp = stamp
    except Exception as error:
        pass
    return self.watcher_poll_frequency if self.watcher_enabled else None


# this is where we store the information for all available components
class ComponentsRegistry(PropertyGroup):

    settings_save_path = ".bevy_components_settings" # where to store data in bpy.texts

    schemaPath: bpy.props.StringProperty(
        name="schema path",
        description="path to the registry schema file",
        default="registry.json"
    )# type: ignore
    schemaFullPath : bpy.props.StringProperty(
        name="schema full path",
        description="path to the registry schema file",
    )# type: ignore
  
    registry: bpy.props. StringProperty(
        name="registry",
        description="component registry"
    )# type: ignore

    missing_type_infos: StringProperty(
        name="missing type infos",
        description="unregistered/missing type infos"
    )# type: ignore

    disable_all_object_updates: BoolProperty(name="disable_object_updates", default=False) # type: ignore

    ## file watcher
    watcher_enabled: BoolProperty(name="Watcher_enabled", default=True, update=toggle_watcher)# type: ignore
    watcher_active: BoolProperty(name = "Flag for watcher status", default = False)# type: ignore

    watcher_poll_frequency: IntProperty(
        name="watcher poll frequency",
        description="frequency (s) at wich to poll for changes to the registry file",
        min=1,
        max=10,
        default=1
    )# type: ignore

    schemaTimeStamp: StringProperty(
        name="last timestamp of schema file",
        description="",
        default=""
    )# type: ignore


    missing_types_list: CollectionProperty(name="missing types list", type=MissingBevyType)# type: ignore
    missing_types_list_index: IntProperty(name = "Index for missing types list", default = 0)# type: ignore

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
        "isize": dict(type=IntProperty, presets=dict()),

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
        "alloc::borrow::Cow<str>": dict(type=StringProperty, presets=dict()),


        "enum":  dict(type=EnumProperty, presets=dict()), 

        'bevy_ecs::entity::Entity': {"type": IntProperty, "presets": {"min":0} },
        'bevy_utils::Uuid':  dict(type=StringProperty, presets=dict()),

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
        "usize":0,

        "i8": 0,
        "i16":0,
        "i32":0,
        "i64":0,
        "i128":0,
        "isize":0,

        "f32": 0.0,
        "f64":0.0,

        "char": " ",
        "str": " ",
        "alloc::string::String": " ",
        "alloc::borrow::Cow<str>":  " ",

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

        'bevy_ecs::entity::Entity': 0,#4294967295, # this is the same as Bevy's Entity::Placeholder, too big for Blender..sigh
        'bevy_utils::Uuid': '"'+str(uuid.uuid4())+'"'

    }

    type_infos = {}
    type_infos_missing = []
    component_propertyGroups = {}
    custom_types_to_add = {}
    invalid_components = []

    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_registry = PointerProperty(type=ComponentsRegistry)
        bpy.context.window_manager.components_registry.watcher_active = False

    @classmethod
    def unregister(cls):
        bpy.context.window_manager.components_registry.watcher_active = False

        for propgroup_name in cls.component_propertyGroups.keys():
            try:
                delattr(ComponentMetadata, propgroup_name)
                #print("unregistered propertyGroup", propgroup_name)
            except Exception as error:
                pass
                #print("failed to remove", error, "ComponentMetadata")
        
        try:
            bpy.app.timers.unregister(watch_schema)
        except Exception as error:
            pass

        del bpy.types.WindowManager.components_registry

    def load_schema(self):
        print("load schema", self)
        # cleanup previous data if any
        self.propGroupIdCounter = 0
        self.long_names_to_propgroup_names.clear()
        self.missing_types_list.clear()
        self.type_infos.clear()
        self.type_infos_missing.clear()
        self.component_propertyGroups.clear()
        self.custom_types_to_add.clear()
        self.invalid_components.clear()

        # now prepare paths to load data
        file_path = bpy.data.filepath
        # Get the folder
        folder_path = os.path.dirname(file_path)
        path =  os.path.join(folder_path, self.schemaPath)
        self.schemaFullPath = path

        f = Path(bpy.path.abspath(path)) # make a path object of abs path
        with open(path) as f: 
            data = json.load(f) 
            defs = data["$defs"]
            self.registry = json.dumps(defs) # FIXME:meh ?

        # start timer
        if not self.watcher_active and self.watcher_enabled:
            self.watcher_active = True
            print("registering function", watch_schema)
            bpy.app.timers.register(watch_schema)


    # we load the json once, so we do not need to do it over & over again
    def load_type_infos(self):
        print("load type infos")
        ComponentsRegistry.type_infos = json.loads(self.registry)
    
    def has_type_infos(self):
        return len(self.type_infos.keys()) != 0

    def load_settings(self):
        print("loading settings")
        settings = load_settings(self.settings_save_path)

        if settings!= None:
            self.schemaPath = settings["components_schemaPath"]
            self.load_schema()
            generate_propertyGroups_for_components()
            ensure_metadata_for_all_objects()


    # we keep a list of component propertyGroup around 
    def register_component_propertyGroup(self, name, propertyGroup):
        self.component_propertyGroups[name] = propertyGroup

    # to be able to give the user more feedback on any missin/unregistered types in their schema file
    def add_missing_typeInfo(self, long_name):
        if not long_name in self.type_infos_missing:
            self.type_infos_missing.append(long_name)
            setattr(self, "missing_type_infos", str(self.type_infos_missing))
            item = self.missing_types_list.add()
            item.long_name = long_name

    def add_custom_type(self, long_name, type_definition):
        self.custom_types_to_add[long_name] = type_definition

    def process_custom_types(self):
        for long_name in self.custom_types_to_add:
            self.type_infos[long_name] = self.custom_types_to_add[long_name]
        self.custom_types_to_add.clear()

    # add an invalid component to the list (long name)
    def add_invalid_component(self, component_name):
        self.invalid_components.append(component_name)


    ###########
        
    propGroupIdCounter: IntProperty(
        name="propGroupIdCounter",
        description="",
        min=0,
        max=1000000000,
        default=0
    ) # type: ignore
    
    long_names_to_propgroup_names = {}

    # generate propGroup name from nesting level & shortName: each shortName + nesting is unique
    def generate_propGroup_name(self, nesting, longName):
        #print("gen propGroup name for", shortName, nesting)
        self.propGroupIdCounter += 1

        propGroupIndex = str(self.propGroupIdCounter)
        propGroupName = propGroupIndex + "_ui"

        key = str(nesting) + longName if len(nesting) > 0 else longName
        self.long_names_to_propgroup_names[key] = propGroupName
        return propGroupName
    
    def get_propertyGroupName_from_longName(self, longName):
        return self.long_names_to_propgroup_names.get(longName, None)
    
    def long_name_to_key():
        pass

    ###########

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