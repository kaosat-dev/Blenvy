import json
import bpy
from bpy_types import (UIList)
from bpy.props import (StringProperty)

from ..components.operators import OT_rename_component
from .operators import(
    COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_ALL, 
    COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_CURRENT, 
    OT_OpenFilebrowser,
    OT_select_component_name_to_replace,
    OT_select_object, ReloadRegistryOperator, 
    COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL, 
    COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT)

class BEVY_COMPONENTS_PT_Configuration(bpy.types.Panel):
    bl_idname = "BEVY_COMPONENTS_PT_Configuration"
    bl_label = "Configuration"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"
    bl_parent_id = "BEVY_COMPONENTS_PT_MainPanel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_description = "list of missing/unregistered type from the bevy side"

    def draw(self, context):
        layout = self.layout
        registry = context.window_manager.components_registry 
      

        row = layout.row()
        col = row.column()
        col.enabled = False
        col.prop(registry, "schemaPath", text="Registry Schema path")
        col = row.column()
        col.operator(OT_OpenFilebrowser.bl_idname, text="Browse for registry schema file (json)")

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
    bl_label = "Advanced tools & configuration"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"
    bl_parent_id = "BEVY_COMPONENTS_PT_MainPanel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_description = "advanced tooling"

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

        row = layout.row()
        col = row.column()
        col.label(text="Status")
        col = row.column()
        col.label(text="Component")
        col = row.column()
        col.label(text="Object")
        col = row.column()
        col.label(text="-----")

        for object in bpy.data.objects: # TODO: very inneficent
            if "components_meta" in object:
                components_metadata = object.components_meta.components
                comp_names = []
                for index, component_meta in enumerate(components_metadata):
                    short_name = component_meta.name
                    if component_meta.invalid:
                        row = layout.row()
                        col = row.column()
                        col.label(text="Invalid")
                        col = row.column()
                        col.label(text=short_name)
                        col = row.column()
                        operator = col.operator(OT_select_object.bl_idname, text=object.name)
                        operator.object_name = object.name

                        col = row.column()
                        operator = col.operator(OT_select_component_name_to_replace.bl_idname, text="select for rename")
                        operator.component_name = short_name

                        if not object.name in objects_with_invalid_components:
                            objects_with_invalid_components.append(object.name)
                        
                        if not short_name in invalid_component_names:
                            invalid_component_names.append(short_name)


                    comp_names.append(short_name) 

                for custom_property in object.keys():
                    if custom_property != 'components_meta' and custom_property not in comp_names:
                        row = layout.row()
                        col = row.column()
                        col.label(text="Unregistered")
                        col = row.column()
                        col.label(text=custom_property)
                        col = row.column()
                        operator = col.operator(OT_select_object.bl_idname, text=object.name)
                        operator.object_name = object.name

                        col = row.column()
                        operator = col.operator(OT_select_component_name_to_replace.bl_idname, text="select for rename")
                        operator.component_name = custom_property

                        if not object.name in objects_with_invalid_components:
                            objects_with_invalid_components.append(object.name)
                        if not short_name in invalid_component_names:
                            invalid_component_names.append(custom_property)
        layout.separator()
        layout.separator()

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
        box.label(text=bpy.context.window_manager.bevy_component_rename_helper.original_name)

        col = row.column()
        col.prop(available_components, "list", text="")
        #row.prop(available_components, "filter",text="Filter")

        col = row.column()
        operator = col.operator(OT_rename_component.bl_idname, text="rename")
        operator.target_objects = json.dumps(objects_with_invalid_components)
        new_name = registry.type_infos[available_components.list]['short_name'] if available_components.list in registry.type_infos else ""
        operator.new_name = new_name

        layout.separator()
        layout.separator()
        row = layout.row()
        box= row.box()
        box.label(text="Conversions between custom properties and components & vice-versa")

        row = layout.row()
        row.label(text="WARNING ! The following operations will overwrite your existing custom properties if they have matching types on the bevy side !")
        row.alert = True

        row = layout.row()
        row.operator(COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT.bl_idname, text="update custom properties of current object" , icon="LOOP_FORWARDS")
        row.enabled = registry_has_type_infos and selected_object is not None

        layout.separator()
        row = layout.row()
        row.operator(COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL.bl_idname, text="update custom properties of ALL objects" , icon="LOOP_FORWARDS")
        row.enabled = registry_has_type_infos

        row = layout.row()
        row.label(text="WARNING ! The following operations will try to overwrite your existing ui values if they have matching types on the bevy side !")
        row.alert = True

        row = layout.row()
        row.operator(COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_CURRENT.bl_idname, text="update UI FROM custom properties of current object" , icon="LOOP_BACK")
        row.enabled = registry_has_type_infos and selected_object is not None

        layout.separator()
        row = layout.row()
        row.operator(COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_ALL.bl_idname, text="update UI FROM custom properties of ALL objects" , icon="LOOP_BACK")
        row.enabled = registry_has_type_infos


class BEVY_COMPONENTS_PT_MissingTypesPanel(bpy.types.Panel):
    """panel listing all the missing bevy types in the schema"""
    bl_idname = "BEVY_COMPONENTS_PT_MissingTypesPanel"
    bl_label = "Bevy Missing/Unregistered Types"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"
    bl_parent_id = "BEVY_COMPONENTS_PT_MainPanel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_description = "list of missing/unregistered type from the bevy side"

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
    )

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
            filtered= helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "type_name", reverse=self.use_filter_name_reverse)

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
            row.prop(item, "type_name", text="")

        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            row = layout.row()
            row.prop(item, "type_name", text="")
