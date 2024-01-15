import bpy
import json
from bpy.props import (StringProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty)
from bpy_types import (PropertyGroup)
from bpy.types import (CollectionProperty)


class ComponentInfos(bpy.types.PropertyGroup):
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


class ComponentsMeta(PropertyGroup):
    infos_per_component:  StringProperty(
        name="infos per component",
        description="component"
    )
    components: bpy.props.CollectionProperty(type = ComponentInfos)  

# We need a collection property of components PER object
def get_component_metadata_by_short_name(object, short_name):
    return next(filter(lambda component: component["name"] == short_name, object.components_meta.components), None)

def cleanup_invalid_metadata(object):
    components_in_object = object.components_meta.components
    to_remove = []
    for index, component_meta in enumerate(components_in_object):
        short_name = component_meta.name
        if short_name not in object.keys():
            print("component:", short_name, "present in metadata, but not in object")
            to_remove.append(index)
    for index in to_remove:
        components_in_object.remove(index)
