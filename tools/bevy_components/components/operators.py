import ast
import json
import bpy
from bpy_types import Operator
from bpy.props import (StringProperty)
from .metadata import add_component_to_object, add_metadata_to_components_without_metadata, find_component_definition_from_short_name

class AddComponentOperator(Operator):
    """Add component to blueprint"""
    bl_idname = "object.addblueprint_to_component"
    bl_label = "Add component to blueprint Operator"
    bl_options = {"UNDO"}

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    )

    def execute(self, context):
        print("adding component to blueprint", self.component_type)
        object = context.object
    
        has_component_type = self.component_type != ""
        if has_component_type and object != None:
            type_infos = context.window_manager.components_registry.type_infos
            component_definition = type_infos[self.component_type]
            add_component_to_object(object, component_definition)

        return {'FINISHED'}

class CopyComponentOperator(Operator):
    """Copy component from blueprint"""
    bl_idname = "object.copy_component"
    bl_label = "Copy component Operator"
    bl_options = {"UNDO"}

    source_component_name: StringProperty(
        name="source component_name",
        description="name of the component to copy",
    )

    source_object_name: StringProperty(
        name="source object name",
        description="name of the object to copy the component from",
    )

    @classmethod
    def register(cls):
        bpy.types.WindowManager.copied_source_component_name = StringProperty()
        bpy.types.WindowManager.copied_source_object = StringProperty()

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.copied_source_component_name
        del bpy.types.WindowManager.copied_source_object
      

    def execute(self, context):
        if self.source_component_name != '' and self.source_object_name != "":
            context.window_manager.copied_source_component_name = self.source_component_name
            context.window_manager.copied_source_object = self.source_object_name
        else:
            self.report({"ERROR"}, "The source object name / component name to copy a component from have not been specified")

        return {'FINISHED'}
    

class PasteComponentOperator(Operator):
    """Paste component to blueprint"""
    bl_idname = "object.paste_component"
    bl_label = "Paste component to blueprint Operator"
    bl_options = {"UNDO"}

    def execute(self, context):
        source_object_name = context.window_manager.copied_source_object
        source_object = bpy.data.objects.get(source_object_name, None)
        print("source object", source_object)
        if source_object == None:
            self.report({"ERROR"}, "The source object to copy a component from does not exist")
        else:
            component_name = context.window_manager.copied_source_component_name
            if not component_name in source_object:
                self.report({"ERROR"}, "The source component to copy a component from does not exist")
            else:
                component_value = source_object[component_name]
                print("pasting component to object: component name:", str(component_name), "component value:" + str(component_value))
                print (context.object)
                component_definition = find_component_definition_from_short_name(component_name)
                add_component_to_object(context.object, component_definition, value = component_value)

        return {'FINISHED'}
    

    
class DeleteComponentOperator(Operator):
    """Delete component from blueprint"""
    bl_idname = "object.delete_component"
    bl_label = "Delete component from blueprint Operator"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to delete",
    )

    def execute(self, context):
        object = context.object
        if object is not None and self.component_name in object: 
            del object[self.component_name]
        else: 
            self.report({"ERROR"}, "The object/ component to remove does not exist")

        return {'FINISHED'}


class GenerateComponent_From_custom_property_Operator(Operator):
    """generate components from custom property"""
    bl_idname = "object.generate_component"
    bl_label = "Generate component from custom_property Operator"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to generate custom properties for",
    )

    def execute(self, context):
        object = context.object
        add_metadata_to_components_without_metadata(object)

        return {'FINISHED'}



class Toggle_ComponentVisibility(Operator):
    """toggles components visibility"""
    bl_idname = "object.toggle_component_visibility"
    bl_label = "Toggle component visibility"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to toggle",
    )

    def execute(self, context):
        object = context.object
        components_in_object = object.components_meta.components
        component_meta =  next(filter(lambda component: component["name"] == self.component_name, components_in_object), None)
        if component_meta != None: 
            component_meta.visible = not component_meta.visible

        return {'FINISHED'}

