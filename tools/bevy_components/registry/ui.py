import bpy
from bpy_types import (UIList)
from .operators import(OT_OpenFilebrowser, ReloadRegistryOperator, COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL, COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT)

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
        selected_object = context.selected_objects[0] if len(context.selected_objects) > 0 else None

        row = layout.row()
        col = row.column()
        col.enabled = False
        col.prop(registry, "schemaPath", text="Schema file path")
        col = row.column()
        col.operator(OT_OpenFilebrowser.bl_idname, text="Browse for schema.json")

        layout.separator()
        layout.operator(ReloadRegistryOperator.bl_idname, text="reload registry" , icon="FILE_REFRESH")

        layout.separator()
        layout.separator()

        row = layout.row()
        row.label(text="WARNING ! The following operations will overwrite your existing custom properties if they have matching types on the bevy side !")
        row.alert = True

        row = layout.row()
        row.operator(COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT.bl_idname, text="update custom properties of current object" , icon="FILE_REFRESH")
        row.enabled = registry.type_infos != None and selected_object is not None

        row = layout.row()
        row.operator(COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL.bl_idname, text="update custom properties of ALL objects" , icon="FILE_REFRESH")
        row.enabled = registry.type_infos != None

        
        
class BEVY_COMPONENTS_PT_MissingTypesPanel(bpy.types.Panel):
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
