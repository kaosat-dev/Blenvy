import bpy
import json
from bpy.props import (StringProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty)
from bpy_types import (PropertyGroup)
from bpy.types import (CollectionProperty)


def add_items_from_collection_callback(self, context):
    items = []
    collection = context.collection
    for index, item in enumerate(collection.component_definitions.values()):
        items.append((str(index), item.name, ""))
    return items

# this one is for UI only, and its inner list contains a useable list of shortnames of components
class ComponentDefinitions(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Collection.components = bpy.props.PointerProperty(type=ComponentDefinitions)

    @classmethod
    def unregister(cls):
        del bpy.types.Collection.components

    list : bpy.props.EnumProperty(
        name="list",
        description="list",
        # items argument required to initialize, just filled with empty values
        items = add_items_from_collection_callback,
    )

class ComponentDefinition(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Collection.component_definitions = bpy.props.CollectionProperty(type=ComponentDefinition)

    @classmethod
    def unregister(cls):
        del bpy.types.Collection.component_definitions

    name : bpy.props.StringProperty(
        name = "name",
        default = ""
    )

    long_name : bpy.props.StringProperty(
        name = "long name",
        default = ""
    )

    type_name : bpy.props.StringProperty(
        name = "Type",
        default = ""
    )

    values: bpy.props.StringProperty(
        name = "Value",
        default = ""
    )

    values: bpy.props.StringProperty(
        name = "Values",
        default = "[]"
    )

    data: bpy.props.StringProperty(
        name = "Toto",
        default = "[]"
    )
    enabled: BoolProperty(
        name="enabled",
        description="component enabled",
        default=True
    )

class ClearComponentDefinitions(bpy.types.Operator):
    ''' clear list of bpy.context.collection.component_definitions '''
    bl_label = "clear component definitions"
    bl_idname = "components.clear_component_definitions"

    def execute(self, context):
        # create a new item, assign its properties
        bpy.context.collection.component_definitions.clear()
        
        return {'FINISHED'}
    

class ComponentMeta(PropertyGroup):
    infos_per_component:  StringProperty(
        name="infos per component",
        description="component"
    )

    components: bpy.props.CollectionProperty(type = ComponentDefinition)  



   

# this is in order to deal with various types of enums
def my_settings_callback(scene, context):

    items = [
        ('LOC', "Location", ""),
        ('ROT', "Rotation", ""),
        ('SCL', "Scale", ""),
    ]
    #items = context.collection.component_enum_values
    print("DYNAMIC ENUM", context.object.components_meta)
    ob = context.object
    """if ob is not None:
        if ob.type == 'LIGHT':
            items.append(('NRG', "Energy", ""))
            items.append(('COL', "Color", ""))"""

    return items




class ComponentEnums(PropertyGroup):

    # apply values to LOC ROT SCL
    transform : EnumProperty(
        name="Apply Data to:",
        description="Apply Data to attribute.",
        items=my_settings_callback
        )
    
class Foos(PropertyGroup):
    toto: EnumProperty(
        name="dyn_enum",
        description="Apply Data to attribute.",
        items=my_settings_callback
    )

class FooBar(PropertyGroup):
    enums: bpy.props.CollectionProperty(type = Foos)  


# We need a collection property of components PER object
def get_component_metadata_by_short_name(object, short_name):
    return next(filter(lambda component: component["name"] == short_name, object.components_meta.components), None)

def cleanup_invalid_metadata(object):
    #registry = bpy.context.window_manager.components_registry.registry 
    #registry = json.loads(registry)
    components_in_object = object.components_meta.components
    to_remove = []
    for index, component_meta in enumerate(components_in_object):
        short_name = component_meta.name
        if short_name not in object.keys():
            print("component:", short_name, "present in metadata, but not in object")
            to_remove.append(index)
    for index in to_remove:
        components_in_object.remove(index)

