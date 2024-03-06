import ast
import json
import bpy
from bpy_types import Operator
from bpy.props import (StringProperty)
from .metadata import add_component_to_object, add_metadata_to_components_without_metadata, apply_customProperty_values_to_object_propertyGroups, copy_propertyGroup_values_to_another_object, find_component_definition_from_short_name, remove_component_from_object

class AddComponentOperator(Operator):
    """Add component to blueprint"""
    bl_idname = "object.add_bevy_component"
    bl_label = "Add component to blueprint Operator"
    bl_options = {"UNDO"}

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    ) # type: ignore

    def execute(self, context):
        object = context.object
        print("adding component ", self.component_type, "to object  '"+object.name+"'")
    
        has_component_type = self.component_type != ""
        if has_component_type and object != None:
            type_infos = context.window_manager.components_registry.type_infos
            component_definition = type_infos[self.component_type]
            add_component_to_object(object, component_definition)

        return {'FINISHED'}

class CopyComponentOperator(Operator):
    """Copy component from blueprint"""
    bl_idname = "object.copy_bevy_component"
    bl_label = "Copy component Operator"
    bl_options = {"UNDO"}

    source_component_name: StringProperty(
        name="source component_name",
        description="name of the component to copy",
    ) # type: ignore

    source_object_name: StringProperty(
        name="source object name",
        description="name of the object to copy the component from",
    ) # type: ignore

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
    bl_idname = "object.paste_bevy_component"
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
                self.report({"ERROR"}, "The source component to copy from does not exist")
            else:
                component_value = source_object[component_name]
                print("pasting component to object: component name:", str(component_name), "component value:" + str(component_value))
                print (context.object)
                registry = context.window_manager.components_registry
                copy_propertyGroup_values_to_another_object(source_object, context.object, component_name, registry)

        return {'FINISHED'}
    
class RemoveComponentOperator(Operator):
    """Remove component from object"""
    bl_idname = "object.remove_bevy_component"
    bl_label = "Remove component from object Operator"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to delete",
    ) # type: ignore

    object_name: StringProperty(
        name="object name",
        description="object whose component to delete",
        default=""
    ) # type: ignore

    def execute(self, context):
        if self.object_name == "":
            object = context.object
        else:
            object = bpy.data.objects[self.object_name]

        print("removing component ", self.component_name, "from object  '"+object.name+"'")

        if object is not None and self.component_name in object: 
            remove_component_from_object(object, self.component_name)
        else: 
            self.report({"ERROR"}, "The object/ component to remove ("+ self.component_name +") does not exist")

        return {'FINISHED'}


class RemoveComponentFromAllObjectsOperator(Operator):
    """Remove component from all object"""
    bl_idname = "object.remove_bevy_component_all"
    bl_label = "Remove component from all objects Operator"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to delete",
    ) # type: ignore

    def execute(self, context):
        print("removing component ", self.component_name, "from all objects")

        for object in bpy.data.objects:
            if len(object.keys()) > 0:
                if object is not None and self.component_name in object: 
                    remove_component_from_object(object, self.component_name)

        return {'FINISHED'}


class RenameHelper(bpy.types.PropertyGroup):
    original_name: bpy.props.StringProperty(name="") # type: ignore
    new_name: bpy.props.StringProperty(name="") # type: ignore

    #object: bpy.props.PointerProperty(type=bpy.types.Object)
    @classmethod
    def register(cls):
        bpy.types.WindowManager.bevy_component_rename_helper = bpy.props.PointerProperty(type=RenameHelper)

    @classmethod
    def unregister(cls):
        # remove handlers & co
        del bpy.types.WindowManager.bevy_component_rename_helper

class OT_rename_component(Operator):
    """Rename component"""
    bl_idname = "object.rename_component"
    bl_label = "rename component"
    bl_options = {"UNDO"}

    original_name: bpy.props.StringProperty(default="") # type: ignore
    new_name: StringProperty(
        name="new_name",
        description="new name of component",
    ) # type: ignore

    target_objects: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        registry = context.window_manager.components_registry
        type_infos = registry.type_infos
        settings = context.window_manager.bevy_component_rename_helper
        original_name = settings.original_name if self.original_name == "" else self.original_name
        new_name = self.new_name

        print("FOO", self.original_name, "fsdf", settings.original_name)

        print("renaming components: original name", original_name, "new_name", self.new_name, "targets", self.target_objects)
        target_objects = json.loads(self.target_objects)
        errors = []
        if original_name != '' and new_name != '' and original_name != new_name and len(target_objects) > 0:
            for object_name in target_objects:
                object = bpy.data.objects[object_name]
                if object and original_name in object:
                    # get metadata
                    components_metadata = getattr(object, "components_meta", None)
                    component_meta = None
                    if components_metadata:
                        components_metadata = components_metadata.components
                        component_meta =  next(filter(lambda component: component["name"] == new_name, components_metadata), None)
                    # copy data to new component, remove the old one
                    try: 
                        object[new_name] = object[original_name]
                        remove_component_from_object(object, original_name)
                    except Exception as error:
                        if '__disable__update' in object:
                            del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
                        if component_meta:
                            component_meta.invalid = True
                            component_meta.invalid_details = "unknow issue when renaming/transforming component, please remove it & add it back again"

                        errors.append( "failed to copy old component value to new component: object: '" + object.name + "', error: " + str(error))
                        
                    try:
                        # attempt conversion
                        long_name = registry.short_names_to_long_names[new_name]
                        component_definition = type_infos[long_name]
                        add_component_to_object(object, component_definition, object[new_name])
                    except Exception as error:
                        if '__disable__update' in object:
                            del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
                        if component_meta:
                            component_meta.invalid = True
                            component_meta.invalid_details = "wrong custom property value, overwrite them by changing the values in the ui or change them & regenerate ('Update UI from ...button')"

                        errors.append( "wrong custom property values to generate target component: object: '" + object.name + "', error: " + str(error))

        if len(errors) > 0:
            self.report({'ERROR'}, "Failed to rename component: Errors:" + str(errors))
        else: 
            self.report({'INFO'}, "Sucessfully renamed component")

        #clear data after we are done
        self.original_name = ""
        context.window_manager.bevy_component_rename_helper.original_name = ""


        return {'FINISHED'}


class GenerateComponent_From_custom_property_Operator(Operator):
    """generate components from custom property"""
    bl_idname = "object.generate_bevy_component_from_custom_property"
    bl_label = "Generate component from custom_property Operator"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to generate custom properties for",
    ) # type: ignore

    def execute(self, context):
        object = context.object

        error = False
        try:
            add_metadata_to_components_without_metadata(object)
            apply_customProperty_values_to_object_propertyGroups(object)
        except Exception as error:
            del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
            error = True
            self.report({'ERROR'}, "Failed to update propertyGroup values from custom property: Error:" + str(error))
        if not error:
            self.report({'INFO'}, "Sucessfully generated UI values for custom properties for selected object")
        return {'FINISHED'}


class Toggle_ComponentVisibility(Operator):
    """toggles components visibility"""
    bl_idname = "object.toggle_bevy_component_visibility"
    bl_label = "Toggle component visibility"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to toggle",
    ) # type: ignore

    def execute(self, context):
        object = context.object
        components_in_object = object.components_meta.components
        component_meta =  next(filter(lambda component: component["name"] == self.component_name, components_in_object), None)
        if component_meta != None: 
            component_meta.visible = not component_meta.visible

        return {'FINISHED'}

