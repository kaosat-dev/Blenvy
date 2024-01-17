import ast
import json
import bpy
from bpy_types import Operator
from bpy.props import (StringProperty, EnumProperty, PointerProperty, FloatVectorProperty)
from .metadata import add_component_to_object, cleanup_invalid_metadata, find_component_definition_from_short_name, get_component_metadata_by_short_name

class AddComponentOperator(Operator):
    """Add component to blueprint"""
    bl_idname = "object.addblueprint_to_component"
    bl_label = "Add component to blueprint Operator"

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    )

    def execute(self, context):
        print("adding component to blueprint", self.component_type)
        object = context.object
        component_definitions = context.window_manager.component_definitions
        component_definition = component_definitions[int(self.component_type)]

        has_component_type = self.component_type != ""
        if has_component_type:
            add_component_to_object(context.object, component_definition)

        return {'FINISHED'}

class CopyComponentOperator(Operator):
    """Copy component from blueprint"""
    bl_idname = "object.copy_component"
    bl_label = "Copy component Operator"


    target_property: StringProperty(
        name="component_name",
        description="component to copy",
    )

    source_object_name: StringProperty()

    def execute(self, context):
        print("copying component to blueprint")

        context.window_manager.copied_source_component_name = self.target_property
        context.window_manager.copied_source_object = self.source_object_name

        return {'FINISHED'}
    

class PasteComponentOperator(Operator):
    """Paste component to blueprint"""
    bl_idname = "object.paste_component"
    bl_label = "Paste component to blueprint Operator"

    def execute(self, context):
        source_object_name = context.window_manager.copied_source_object
        source_object = bpy.data.objects[source_object_name]
        component_name = context.window_manager.copied_source_component_name
        component_value = source_object[component_name]
        print("pasting component to object", component_name, component_value)
        print (context.object)
        component_definition = find_component_definition_from_short_name(component_name)
        add_component_to_object(context.object, component_definition, value = component_value)

        return {'FINISHED'}
    

    
class DeleteComponentOperator(Operator):
    """Delete component from blueprint"""
    bl_idname = "object.delete_component"
    bl_label = "Delete component from blueprint Operator"
    bl_options = {"REGISTER", "UNDO"}

    target_property: StringProperty(
        name="component_name",
        description="component to delete",
    )

    def execute(self, context):
        print("delete component to blueprint")
        print (context.object)

        # fixme: refactor, do this better
        object = context.object      
        if object is not None: 
            del object[self.target_property]

        return {'FINISHED'}