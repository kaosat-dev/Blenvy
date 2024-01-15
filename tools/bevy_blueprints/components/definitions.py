import bpy
import json
from bpy.props import (StringProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty)
from bpy_types import (PropertyGroup)
from bpy.types import (CollectionProperty)

class ComponentDefinition(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.WindowManager.component_definitions = bpy.props.CollectionProperty(type=ComponentDefinition)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.component_definitions

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


