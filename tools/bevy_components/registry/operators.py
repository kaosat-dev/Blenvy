import os
import bpy
from bpy_types import (Operator)
from bpy.props import (StringProperty)
from bpy_extras.io_utils import ImportHelper

from ..helpers import upsert_settings
from ..components.metadata import apply_customProperty_values_to_object_propertyGroups, apply_propertyGroup_values_to_object_customProperties, ensure_metadata_for_all_objects
from ..propGroups.prop_groups import generate_propertyGroups_for_components

class ReloadRegistryOperator(Operator):
    """Reloads registry (schema file) from disk, generates propertyGroups for components & ensures all objects have metadata """
    bl_idname = "object.reload_registry"
    bl_label = "Reload Registry"
    bl_options = {"UNDO"}

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    ) # type: ignore

    def execute(self, context):
        print("reload registry")
        context.window_manager.components_registry.load_schema()
        generate_propertyGroups_for_components()
        print("")
        print("")
        print("")
        ensure_metadata_for_all_objects()

        # now force refresh the ui
        for area in context.screen.areas: 
            for region in area.regions:
                if region.type == "UI":
                    region.tag_redraw()

        return {'FINISHED'}
    
class COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL(Operator):
    """Apply registry to ALL objects: update the custom property values of all objects based on their definition, if any"""
    bl_idname = "object.refresh_custom_properties_all"
    bl_label = "Apply Registry to all objects"
    bl_options = {"UNDO"}

    def execute(self, context):
        print("apply registry to all")
        #context.window_manager.components_registry.load_schema()
        for object in bpy.data.objects:
            apply_propertyGroup_values_to_object_customProperties(object)

        return {'FINISHED'}
    
class COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT(Operator):
    """Apply registry to CURRENT object: update the custom property values of current object based on their definition, if any"""
    bl_idname = "object.refresh_custom_properties_current"
    bl_label = "Apply Registry to current object"
    bl_options = {"UNDO"}

    def execute(self, context):
        print("apply registry to current object")
        object = context.object
        apply_propertyGroup_values_to_object_customProperties(object)
        return {'FINISHED'}
    

class COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_CURRENT(Operator):
    """Update UI values from custom properties to CURRENT object"""
    bl_idname = "object.refresh_ui_from_custom_properties_current"
    bl_label = "Apply custom_properties to current object"
    bl_options = {"UNDO"}

    def execute(self, context):
        print("apply custom properties to current object")
        object = context.object
        error = False
        try:
            apply_customProperty_values_to_object_propertyGroups(object)
        except Exception as error:
            del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
            error = True
            self.report({'ERROR'}, "Failed to update propertyGroup values from custom property: Error:" + str(error))
        if not error:
            self.report({'INFO'}, "Sucessfully generated UI values for custom properties for selected object")

        return {'FINISHED'}
    
class COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_ALL(Operator):
    """Update UI values from custom properties to ALL object"""
    bl_idname = "object.refresh_ui_from_custom_properties_all"
    bl_label = "Apply custom_properties to all objects"
    bl_options = {"UNDO"}

    def execute(self, context):
        print("apply custom properties to all object")
        bpy.context.window_manager.components_registry.disable_all_object_updates = True
        errors = []
        for object in bpy.data.objects:
            try:
                apply_customProperty_values_to_object_propertyGroups(object)
            except Exception as error:
                del object["__disable__update"] # make sure custom properties are updateable afterwards, even in the case of failure
                errors.append( "object: '" + object.name + "', error: " + str(error))
        if len(errors) > 0:
            self.report({'ERROR'}, "Failed to update propertyGroup values from custom property: Errors:" + str(errors))
        else: 
            self.report({'INFO'}, "Sucessfully generated UI values for custom properties for all objects")
        bpy.context.window_manager.components_registry.disable_all_object_updates = False


        return {'FINISHED'}

class OT_OpenFilebrowser(Operator, ImportHelper):
    """Browse for registry json file"""
    bl_idname = "generic.open_filebrowser" 
    bl_label = "Open the file browser" 

    filter_glob: StringProperty( 
        default='*.json', 
        options={'HIDDEN'} 
    ) # type: ignore
    def execute(self, context): 
        """Do something with the selected file(s)."""
        #filename, extension = os.path.splitext(self.filepath) 
        file_path = bpy.data.filepath
        # Get the folder
        folder_path = os.path.dirname(file_path)
        relative_path = os.path.relpath(self.filepath, folder_path)

        registry = context.window_manager.components_registry
        registry.schemaPath = relative_path

        upsert_settings(registry.settings_save_path, {"schemaPath": relative_path})
        
        return {'FINISHED'}
    
