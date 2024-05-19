import ast
import json
import bpy
from bpy_types import Operator
from bpy.props import (StringProperty)

from .metadata import add_component_from_custom_property, add_component_to_item, apply_propertyGroup_values_to_item_customProperties_for_component, copy_propertyGroup_values_to_another_item, get_bevy_component_value_by_long_name, get_bevy_components, is_bevy_component_in_item, remove_component_from_item, rename_component, toggle_component
from ..utils import get_selected_object_or_collection

class AddComponentOperator(Operator):
    """Add Bevy component to object/collection"""
    bl_idname = "object.add_bevy_component"
    bl_label = "Add component to object/collection Operator"
    bl_options = {"UNDO"}

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    ) # type: ignore

    def execute(self, context):
        target = get_selected_object_or_collection(context)
        print("adding component ", self.component_type, "to target  '"+target.name+"'")
    
        has_component_type = self.component_type != ""
        if has_component_type and target != None:
            type_infos = context.window_manager.components_registry.type_infos
            component_definition = type_infos[self.component_type]
            add_component_to_item(target, component_definition)

        return {'FINISHED'}

class CopyComponentOperator(Operator):
    """Copy Bevy component from object"""
    bl_idname = "object.copy_bevy_component"
    bl_label = "Copy component Operator"
    bl_options = {"UNDO"}

    source_component_name: StringProperty(
        name="source component_name (long)",
        description="name of the component to copy",
    ) # type: ignore

    source_item_name: StringProperty(
        name="source item name",
        description="name of the object/collection to copy the component from",
    ) # type: ignore

    source_item_type: StringProperty(
        name="source item type",
        description="type of the object/collection to copy the component from",
    ) # type: ignore

    @classmethod
    def register(cls):
        bpy.types.WindowManager.copied_source_component_name = StringProperty()
        bpy.types.WindowManager.copied_source_item_name = StringProperty()
        bpy.types.WindowManager.copied_source_item_type = StringProperty()

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.copied_source_component_name
        del bpy.types.WindowManager.copied_source_item_name
        del bpy.types.WindowManager.copied_source_item_type


    def execute(self, context):
        if self.source_component_name != '' and self.source_item_name != "" and self.source_item_type != "":
            context.window_manager.copied_source_component_name = self.source_component_name
            context.window_manager.copied_source_item_name = self.source_item_name
            context.window_manager.copied_source_item_type = self.source_item_type
        else:
            self.report({"ERROR"}, "The source object/collection name or component name to copy a component from have not been specified")

        return {'FINISHED'}
    

class PasteComponentOperator(Operator):
    """Paste Bevy component to object"""
    bl_idname = "object.paste_bevy_component"
    bl_label = "Paste component to object Operator"
    bl_options = {"UNDO"}

    def execute(self, context):
        source_item_name = context.window_manager.copied_source_item_name
        source_item_type = context.window_manager.copied_source_item_type
        if source_item_type == 'Object':
            source_item = bpy.data.objects.get(source_item_name, None)
        elif source_item_type == 'Collection':
            source_item = bpy.data.collections.get(source_item_name, None)

        if source_item == None:
            self.report({"ERROR"}, "The source object to copy a component from does not exist")
        else:
            component_name = context.window_manager.copied_source_component_name
            component_value = get_bevy_component_value_by_long_name(source_item, component_name)
            if component_value is None:
                self.report({"ERROR"}, "The source component to copy from does not exist")
            else:
                print("pasting component to item:", source_item, "component name:", str(component_name), "component value:" + str(component_value))
                registry = context.window_manager.components_registry
                target_item = get_selected_object_or_collection(context)
                copy_propertyGroup_values_to_another_item(source_item, target_item, component_name, registry)

        return {'FINISHED'}
    
class RemoveComponentOperator(Operator):
    """Remove Bevy component from object/collection"""
    bl_idname = "object.remove_bevy_component"
    bl_label = "Remove component from object/collection Operator"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to delete",
    ) # type: ignore

    item_name: StringProperty(
        name="object name",
        description="object whose component to delete",
        default=""
    ) # type: ignore

    item_type: StringProperty(
        name="item type",
        description="type of the object/collection to delete",
    ) # type: ignore

    def execute(self, context):
        target = None
        if self.item_name == "":
            self.report({"ERROR"}, "The target to remove ("+ self.component_name +") from does not exist")
        else:
            if self.item_type == 'Object':
                target = bpy.data.objects[self.item_name]
            elif self.item_type == 'Collection':
                target = bpy.data.collections[self.item_name]

        print("removing component ", self.component_name, "from object  '"+target.name+"'")

        if target is not None and 'bevy_components' in target :
            component_value = get_bevy_component_value_by_long_name(target, self.component_name)
            if component_value is not None:
                remove_component_from_item(target, self.component_name)
            else :
                self.report({"ERROR"}, "The component to remove ("+ self.component_name +") does not exist")
        else: 
            self.report({"ERROR"}, "The target to remove ("+ self.component_name +") from does not exist")
        return {'FINISHED'}


class RemoveComponentFromAllItemsOperator(Operator):
    """Remove Bevy component from all items"""
    bl_idname = "object.remove_bevy_component_all"
    bl_label = "Remove component from all items Operator"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name (long name)",
        description="component to delete",
    ) # type: ignore

    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_remove_progress = bpy.props.FloatProperty(default=-1.0)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.components_remove_progress

    def execute(self, context):
        print("removing component ", self.component_name, "from all objects/collections")
        total = len(bpy.data.objects) + len(bpy.data.collections)
        for index, object in enumerate(bpy.data.objects):
            if len(object.keys()) > 0:
                if object is not None and is_bevy_component_in_item(object, self.component_name): 
                    remove_component_from_item(object, self.component_name)
            
            progress = index / total
            context.window_manager.components_remove_progress = progress
            # now force refresh the ui
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        for index, collection in enumerate(bpy.data.collections):
            if len(collection.keys()) > 0:
                if collection is not None and is_bevy_component_in_item(collection, self.component_name): 
                    remove_component_from_item(collection, self.component_name)
            
            progress = index / total
            context.window_manager.components_remove_progress = progress
            # now force refresh the ui
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
        context.window_manager.components_remove_progress = -1.0

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
    """Rename Bevy component"""
    bl_idname = "object.rename_bevy_component"
    bl_label = "rename component"
    bl_options = {"UNDO"}

    original_name: bpy.props.StringProperty(default="") # type: ignore
    new_name: StringProperty(
        name="new_name",
        description="new name of component",
    ) # type: ignore

    target_objects: bpy.props.StringProperty() # type: ignore

    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_rename_progress = bpy.props.FloatProperty(default=-1.0) #bpy.props.PointerProperty(type=RenameHelper)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.components_rename_progress

    def execute(self, context):
        registry = context.window_manager.components_registry
        type_infos = registry.type_infos
        settings = context.window_manager.bevy_component_rename_helper
        original_name = settings.original_name if self.original_name == "" else self.original_name
        new_name = self.new_name


        print("renaming components: original name", original_name, "new_name", self.new_name, "targets", self.target_objects)
        target_objects = json.loads(self.target_objects)
        errors = []
        total = len(target_objects)

        if original_name != '' and new_name != '' and original_name != new_name and len(target_objects) > 0:
            for index, item_name in enumerate(target_objects):
                object = bpy.data.objects[item_name]
                if object and original_name in get_bevy_components(object) or original_name in object:
                    try:
                        # attempt conversion
                        rename_component(object=object, original_long_name=original_name, new_long_name=new_name)
                    except Exception as error:
                        if '__disable__update' in object:
                            del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
                        components_metadata = getattr(object, "components_meta", None)
                        if components_metadata:
                            components_metadata = components_metadata.components
                            component_meta =  next(filter(lambda component: component["long_name"] == new_name, components_metadata), None)
                            if component_meta:
                                component_meta.invalid = True
                                component_meta.invalid_details = "wrong custom property value, overwrite them by changing the values in the ui or change them & regenerate"

                        errors.append( "wrong custom property values to generate target component: object: '" + object.name + "', error: " + str(error))
                
                progress = index / total
                context.window_manager.components_rename_progress = progress

                try:
                    # now force refresh the ui
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                except: pass # this is to allow this to run in cli/headless mode

        if len(errors) > 0:
            self.report({'ERROR'}, "Failed to rename component: Errors:" + str(errors))
        else: 
            self.report({'INFO'}, "Sucessfully renamed component")

        #clear data after we are done
        self.original_name = ""
        context.window_manager.bevy_component_rename_helper.original_name = ""
        context.window_manager.components_rename_progress = -1.0

        return {'FINISHED'}


class GenerateComponent_From_custom_property_Operator(Operator):
    """Generate Bevy components from custom property"""
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
            add_component_from_custom_property(object)
        except Exception as error:
            del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
            error = True
            self.report({'ERROR'}, "Failed to update propertyGroup values from custom property: Error:" + str(error))
        if not error:
            self.report({'INFO'}, "Sucessfully generated UI values for custom properties for selected object")
        return {'FINISHED'}


class Fix_Component_Operator(Operator):
    """Attempt to fix Bevy component"""
    bl_idname = "object.fix_bevy_component"
    bl_label = "Fix component (attempts to)"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to fix",
    ) # type: ignore

    def execute(self, context):
        object = context.object
        error = False
        try:
            apply_propertyGroup_values_to_item_customProperties_for_component(object, self.component_name)
        except Exception as error:
            if "__disable__update" in object:
                del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
            error = True
            self.report({'ERROR'}, "Failed to fix component: Error:" + str(error))
        if not error:
            self.report({'INFO'}, "Sucessfully fixed component (please double check component & its custom property value)")
        return {'FINISHED'}

class Toggle_ComponentVisibility(Operator):
    """Toggle Bevy component's visibility"""
    bl_idname = "object.toggle_bevy_component_visibility"
    bl_label = "Toggle component visibility"
    bl_options = {"UNDO"}

    component_name: StringProperty(
        name="component name",
        description="component to toggle",
    ) # type: ignore

    def execute(self, context):
        target = get_selected_object_or_collection(context)
        toggle_component(target, self.component_name)
        return {'FINISHED'}

