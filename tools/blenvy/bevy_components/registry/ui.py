import json
import bpy
from bpy_types import (UIList)
from bpy.props import (StringProperty)

from ..components.operators import OT_rename_component, RemoveComponentFromAllObjectsOperator, RemoveComponentOperator
from .operators import(
    COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_ALL, 
    COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_CURRENT, 
    OT_OpenSchemaFileBrowser,
    OT_select_component_name_to_replace,
    OT_select_object, ReloadRegistryOperator, 
    COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL, 
    COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT)

class BEVY_COMPONENTS_PT_Configuration(bpy.types.Panel):
    bl_idname = "BEVY_COMPONENTS_PT_Configuration"
    bl_label = "Components"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"
    bl_parent_id = "BLENVY_PT_SidePanel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_description = "list of missing/unregistered type from the bevy side"

    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'SETTINGS'
        return context.object is not None 

    def draw(self, context):
        layout = self.layout
        registry = context.window_manager.components_registry 
      

        row = layout.row()
        col = row.column()
        col.enabled = False
        col.prop(registry, "schemaPath", text="Registry Schema path")
        col = row.column()
        col.operator(OT_OpenSchemaFileBrowser.bl_idname, text="Browse for registry schema file (json)")

        layout.separator()
        layout.operator(ReloadRegistryOperator.bl_idname, text="reload registry" , icon="FILE_REFRESH")

        layout.separator()
        row = layout.row()
        
        row.prop(registry, "watcher_enabled", text="enable registry file polling")
        row.prop(registry, "watcher_poll_frequency", text="registry file poll frequency (s)")

        layout.separator()
        layout.separator()

        
class BEVY_COMPONENTS_PT_AdvancedToolsPanel(bpy.types.Panel):
    """panel listing all the missing bevy types in the schema"""
    bl_idname = "BEVY_COMPONENTS_PT_AdvancedToolsPanel"
    bl_label = "Advanced tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"
    bl_parent_id = "BLENVY_PT_SidePanel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_description = "advanced tooling"

    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'TOOLS'

    def draw_invalid_or_unregistered_header(self, layout, items):
        row = layout.row()

        for item in items:
            col = row.column()
            col.label(text=item)


    def draw_invalid_or_unregistered(self, layout, status, component_name, object):
        available_components = bpy.context.window_manager.components_list
        registry = bpy.context.window_manager.components_registry 
        registry_has_type_infos = registry.has_type_infos()

        row = layout.row()

        col = row.column()
        col.label(text=component_name)

        col = row.column()
        operator = col.operator(OT_select_object.bl_idname, text=object.name)
        operator.object_name = object.name

        col = row.column()
        col.label(text=status)

        col = row.column()
        col.prop(available_components, "list", text="")

        col = row.column()
        operator = col.operator(OT_rename_component.bl_idname, text="", icon="SHADERFX") #rename
        new_name = registry.type_infos[available_components.list]['long_name'] if available_components.list in registry.type_infos else ""
        operator.original_name = component_name
        operator.target_objects = json.dumps([object.name])
        operator.new_name = new_name
        col.enabled = registry_has_type_infos and component_name != "" and component_name != new_name


        col = row.column()
        operator = col.operator(RemoveComponentOperator.bl_idname, text="", icon="X")
        operator.object_name = object.name
        operator.component_name = component_name

        col = row.column()
        col = row.column()
        operator = col.operator(OT_select_component_name_to_replace.bl_idname, text="", icon="EYEDROPPER") #text="select for rename", 
        operator.component_name = component_name

    def draw(self, context):
        layout = self.layout
        registry = bpy.context.window_manager.components_registry 
        registry_has_type_infos = registry.has_type_infos()
        selected_object = context.selected_objects[0] if len(context.selected_objects) > 0 else None
        available_components = bpy.context.window_manager.components_list

        row = layout.row()
        box= row.box()
        box.label(text="Invalid/ unregistered components")

        objects_with_invalid_components = []
        invalid_component_names = []

        self.draw_invalid_or_unregistered_header(layout, ["Component", "Object", "Status", "Target"])

        for object in bpy.data.objects: # TODO: very inneficent
            if len(object.keys()) > 0:
                if "components_meta" in object:
                    components_metadata = object.components_meta.components
                    comp_names = []
                    for index, component_meta in enumerate(components_metadata):
                        long_name = component_meta.long_name
                        if component_meta.invalid:
                            self.draw_invalid_or_unregistered(layout, "Invalid", long_name, object)
                        
                            if not object.name in objects_with_invalid_components:
                                objects_with_invalid_components.append(object.name)
                            
                            if not long_name in invalid_component_names:
                                invalid_component_names.append(long_name)


                        comp_names.append(long_name) 

                    for custom_property in object.keys():
                        if custom_property != 'components_meta' and custom_property != 'bevy_components' and custom_property not in comp_names:
                            self.draw_invalid_or_unregistered(layout, "Unregistered", custom_property, object)

                            if not object.name in objects_with_invalid_components:
                                objects_with_invalid_components.append(object.name)
                            """if not long_name in invalid_component_names:
                                invalid_component_names.append(custom_property)""" # FIXME
        layout.separator()
        layout.separator()
        original_name = bpy.context.window_manager.bevy_component_rename_helper.original_name

        row = layout.row()
        col = row.column()
        col.label(text="Original")
        col = row.column()
        col.label(text="New")
        col = row.column()
        col.label(text="------")

        row = layout.row()
        col = row.column()
        box = col.box()
        box.label(text=original_name)

        col = row.column()
        col.prop(available_components, "list", text="")
        #row.prop(available_components, "filter",text="Filter")
    
        col = row.column()
        components_rename_progress = context.window_manager.components_rename_progress

        if components_rename_progress == -1.0:
            operator = col.operator(OT_rename_component.bl_idname, text="apply", icon="SHADERFX")
            operator.target_objects = json.dumps(objects_with_invalid_components)
            new_name = registry.type_infos[available_components.list]['short_name'] if available_components.list in registry.type_infos else ""
            operator.new_name = new_name
            col.enabled = registry_has_type_infos and original_name != "" and original_name != new_name
        else:
            if hasattr(layout,"progress") : # only for Blender > 4.0
                col.progress(factor = components_rename_progress, text=f"updating {components_rename_progress * 100.0:.2f}%")

        col = row.column()
        remove_components_progress = context.window_manager.components_remove_progress
        if remove_components_progress == -1.0:
            operator = row.operator(RemoveComponentFromAllObjectsOperator.bl_idname, text="", icon="X")
            operator.component_name = context.window_manager.bevy_component_rename_helper.original_name
            col.enabled = registry_has_type_infos and original_name != ""
        else:
            if hasattr(layout,"progress") : # only for Blender > 4.0
                col.progress(factor = remove_components_progress, text=f"updating {remove_components_progress * 100.0:.2f}%")

        layout.separator()
        layout.separator()
        row = layout.row()
        box= row.box()
        box.label(text="Conversions between custom properties and components & vice-versa")

        row = layout.row()
        row.label(text="WARNING ! The following operations will overwrite your existing custom properties if they have matching types on the bevy side !")
        row.alert = True

        ##
        row = layout.row()
        custom_properties_from_components_progress_current = context.window_manager.custom_properties_from_components_progress

        if custom_properties_from_components_progress_current == -1.0:
            row.operator(COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT.bl_idname, text="update custom properties of current object" , icon="LOOP_FORWARDS")
            row.enabled = registry_has_type_infos and selected_object is not None
        else:
            if hasattr(layout,"progress") : # only for Blender > 4.0
                layout.progress(factor = custom_properties_from_components_progress_current, text=f"updating {custom_properties_from_components_progress_current * 100.0:.2f}%")

        layout.separator()
        row = layout.row()
        custom_properties_from_components_progress_all = context.window_manager.custom_properties_from_components_progress_all

        if custom_properties_from_components_progress_all == -1.0:
            row.operator(COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL.bl_idname, text="update custom properties of ALL objects" , icon="LOOP_FORWARDS")
            row.enabled = registry_has_type_infos
        else:
            if hasattr(layout,"progress") : # only for Blender > 4.0
                layout.progress(factor = custom_properties_from_components_progress_all, text=f"updating {custom_properties_from_components_progress_all * 100.0:.2f}%")

        ########################

        row = layout.row()
        row.label(text="WARNING ! The following operations will try to overwrite your existing ui values if they have matching types on the bevy side !")
        row.alert = True

        components_from_custom_properties_progress_current = context.window_manager.components_from_custom_properties_progress

        row = layout.row()
        if components_from_custom_properties_progress_current == -1.0:
            row.operator(COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_CURRENT.bl_idname, text="update UI FROM custom properties of current object" , icon="LOOP_BACK")
            row.enabled = registry_has_type_infos and selected_object is not None
        else:
            if hasattr(layout,"progress") : # only for Blender > 4.0
                layout.progress(factor = components_from_custom_properties_progress_current, text=f"updating {components_from_custom_properties_progress_current * 100.0:.2f}%")

        layout.separator()
        row = layout.row()
        components_from_custom_properties_progress_all = context.window_manager.components_from_custom_properties_progress_all

        if components_from_custom_properties_progress_all == -1.0:
            row.operator(COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_ALL.bl_idname, text="update UI FROM custom properties of ALL objects" , icon="LOOP_BACK")
            row.enabled = registry_has_type_infos
        else:
            if hasattr(layout,"progress") : # only for Blender > 4.0
                layout.progress(factor = components_from_custom_properties_progress_all, text=f"updating {components_from_custom_properties_progress_all * 100.0:.2f}%")


class BEVY_COMPONENTS_PT_MissingTypesPanel(bpy.types.Panel):
    """panel listing all the missing bevy types in the schema"""
    bl_idname = "BEVY_COMPONENTS_PT_MissingTypesPanel"
    bl_label = "Missing/Unregistered Types"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"
    bl_parent_id = "BLENVY_PT_SidePanel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_description = "list of missing/unregistered type from the bevy side"

    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'TOOLS'

    def draw(self, context):
        layout = self.layout
        registry = bpy.context.window_manager.components_registry 

        layout.label(text="Missing types ")
        layout.template_list("MISSING_TYPES_UL_List", "Missing types list", registry, "missing_types_list", registry, "missing_types_list_index")


class MISSING_TYPES_UL_List(UIList): 
    """Missing components UIList.""" 

    use_filter_name_reverse: bpy.props.BoolProperty(
        name="Reverse Name",
        default=False,
        options=set(),
        description="Reverse name filtering",
    ) # type: ignore

    use_order_name = bpy.props.BoolProperty(name="Name", default=False, options=set(),
                                            description="Sort groups by their name (case-insensitive)")

    def filter_items__(self, context, data, propname): 
        """Filter and order items in the list.""" 
        # We initialize filtered and ordered as empty lists. Notice that # if all sorting and filtering is disabled, we will return # these empty. 
        filtered = [] 
        ordered = [] 
        items = getattr(data, propname)

        helper_funcs = bpy.types.UI_UL_list


        print("filter, order", items, self, dict(self))
        if self.filter_name:
            print("ssdfs", self.filter_name)
            filtered= helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "long_name", reverse=self.use_filter_name_reverse)

        if not filtered:
            filtered = [self.bitflag_filter_item] * len(items)

        if self.use_order_name:
            ordered = helper_funcs.sort_items_by_name(items, "name")
        

        return filtered, ordered 


    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            row = layout.row()
            #row.enabled = False
            #row.alert = True
            row.prop(item, "long_name", text="")

        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            row = layout.row()
            row.prop(item, "long_name", text="")
