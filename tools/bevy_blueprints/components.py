import bpy
import json
from bpy.props import (StringProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty)


def add_items_from_collection_callback(self, context):
    items = []
    scene = context.collection
    for index, item in enumerate(scene.component_definitions.values()):
        items.append((str(index), item.name, ""))
    return items


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

    toto: bpy.props.StringProperty(
        name = "Toto",
        default = "[]"
    )

class AddComponentDefinitions(bpy.types.Operator):
    ''' add item to bpy.context.collection.component_definitions '''
    bl_label = "add item"
    bl_idname = "components.add_component_definitions"

    component_name: StringProperty(
        name="component_name",
        description="component type to add",
    )

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    )

    component_values: StringProperty(
        name="component_values",
        description="component values to add",
    )

    def execute(self, context):
        # create a new item, assign its properties
        item = bpy.context.collection.component_definitions.add()
        item.name = self.component_name#"Dynamic"
        item.type_name = self.component_type#"Bool"
        item.values = self.component_values#"Bool"

        return {'FINISHED'}
    
class ClearComponentDefinitions(bpy.types.Operator):
    ''' clear list of bpy.context.collection.component_definitions '''
    bl_label = "clear component definitions"
    bl_idname = "components.clear_component_definitions"

    def execute(self, context):
        # create a new item, assign its properties
        bpy.context.collection.component_definitions.clear()
        
        return {'FINISHED'}