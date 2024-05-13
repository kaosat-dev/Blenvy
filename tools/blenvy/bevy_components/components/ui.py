import json
import bpy

from ..registry.operators import COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT
from .metadata import do_object_custom_properties_have_missing_metadata, get_bevy_components
from .operators import AddComponentOperator, CopyComponentOperator, Fix_Component_Operator, RemoveComponentOperator, GenerateComponent_From_custom_property_Operator, PasteComponentOperator, Toggle_ComponentVisibility
   
def draw_propertyGroup( propertyGroup, layout, nesting =[], rootName=None):
    is_enum = getattr(propertyGroup, "with_enum")
    is_list = getattr(propertyGroup, "with_list") 
    is_map = getattr(propertyGroup, "with_map")
    # item in our components hierarchy can get the correct propertyGroup by STRINGS because of course, we cannot pass objects to operators...sigh

    # if it is an enum, the first field name is always the list of enum variants, the others are the variants
    field_names = propertyGroup.field_names
    #print("")
    #print("drawing", propertyGroup, nesting, "component_name", rootName)
    if is_enum:
        subrow = layout.row()
        display_name = field_names[0] if propertyGroup.tupple_or_struct == "struct" else ""
        subrow.prop(propertyGroup, field_names[0], text=display_name)
        subrow.separator()
        selection = getattr(propertyGroup, "selection")

        for fname in field_names[1:]:
            if fname == "variant_" + selection:
                subrow = layout.row()
                display_name = fname if propertyGroup.tupple_or_struct == "struct" else ""

                nestedPropertyGroup = getattr(propertyGroup, fname)
                nested = getattr(nestedPropertyGroup, "nested", False)
                #print("nestedPropertyGroup", nestedPropertyGroup, fname, nested)
                if nested:
                    draw_propertyGroup(nestedPropertyGroup, subrow.column(), nesting + [fname], rootName )
                # if an enum variant is not a propertyGroup
                break
    elif is_list:
        item_list = getattr(propertyGroup, "list")
        list_index = getattr(propertyGroup, "list_index")
        box = layout.box()
        split = box.split(factor=0.9)
        list_column, buttons_column = (split.column(),split.column())

        list_column = list_column.box()
        for index, item  in enumerate(item_list):
            row = list_column.row()
            draw_propertyGroup(item, row, nesting, rootName)
            icon = 'CHECKBOX_HLT' if list_index == index else 'CHECKBOX_DEHLT'
            op = row.operator('generic_list.select_item', icon=icon, text="")
            op.component_name = rootName
            op.property_group_path = json.dumps(nesting)
            op.selection_index = index

        #various control buttons
        buttons_column.separator()
        row = buttons_column.row()
        op = row.operator('generic_list.list_action', icon='ADD', text="")
        op.action = 'ADD'
        op.component_name = rootName
        op.property_group_path = json.dumps(nesting)

        row = buttons_column.row()
        op = row.operator('generic_list.list_action', icon='REMOVE', text="")
        op.action = 'REMOVE'
        op.component_name = rootName
        op.property_group_path = json.dumps(nesting)

        buttons_column.separator()
        row = buttons_column.row()
        op = row.operator('generic_list.list_action', icon='TRIA_UP', text="")
        op.action = 'UP'
        op.component_name = rootName
        op.property_group_path = json.dumps(nesting)

        row = buttons_column.row()
        op = row.operator('generic_list.list_action', icon='TRIA_DOWN', text="")
        op.action = 'DOWN'
        op.component_name = rootName
        op.property_group_path = json.dumps(nesting)

    elif is_map:
        root = layout.row().column()
        if hasattr(propertyGroup, "list"): # TODO: improve handling of non drawable UI
            keys_list = getattr(propertyGroup, "list")
            values_list = getattr(propertyGroup, "values_list")
            box = root.box()
            row = box.row()
            row.label(text="Add entry:")
            keys_setter = getattr(propertyGroup, "keys_setter")
            draw_propertyGroup(keys_setter, row, nesting, rootName)

            values_setter = getattr(propertyGroup, "values_setter")
            draw_propertyGroup(values_setter, row, nesting, rootName)

            op = row.operator('generic_map.map_action', icon='ADD', text="")
            op.action = 'ADD'
            op.component_name = rootName
            op.property_group_path = json.dumps(nesting)

            box = root.box()
            split = box.split(factor=0.9)
            list_column, buttons_column = (split.column(),split.column())
            list_column = list_column.box()

            for index, item  in enumerate(keys_list):
                row = list_column.row()
                draw_propertyGroup(item, row, nesting, rootName)

                value = values_list[index]
                draw_propertyGroup(value, row, nesting, rootName)

                op = row.operator('generic_map.map_action', icon='REMOVE', text="")
                op.action = 'REMOVE'
                op.component_name = rootName
                op.property_group_path = json.dumps(nesting)
                op.target_index = index


            #various control buttons
            buttons_column.separator()
            row = buttons_column.row()
        

    else: 
        for fname in field_names:
            #subrow = layout.row()
            nestedPropertyGroup = getattr(propertyGroup, fname)
            nested = getattr(nestedPropertyGroup, "nested", False)
            display_name = fname if propertyGroup.tupple_or_struct == "struct" else ""

            if nested:
                layout.separator()
                layout.separator()

                layout.label(text=display_name) #  this is the name of the field/sub field
                layout.separator()
                subrow = layout.row()
                draw_propertyGroup(nestedPropertyGroup, subrow, nesting + [fname], rootName )
            else:
                subrow = layout.row()
                subrow.prop(propertyGroup, fname, text=display_name)
                subrow.separator()


class BEVY_COMPONENTS_PT_ComponentsPanel(bpy.types.Panel):
    bl_idname = "BEVY_COMPONENTS_PT_ComponentsPanel"
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"
    bl_parent_id = "BLENVY_PT_SidePanel"

    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'COMPONENTS'
        return context.object is not None 

    def draw_header(self, context):
        layout = self.layout
        name = context.object.name if context.object != None else ''
        layout.label(text="Components For "+ name)

    def draw(self, context):
        object = context.object
        layout = self.layout

        # we get & load our component registry
        registry = bpy.context.window_manager.components_registry 
        available_components = bpy.context.window_manager.components_list
        registry_has_type_infos = registry.has_type_infos()

        if object is not None:
            row = layout.row(align=True)
            row.prop(available_components, "list", text="Component")
            row.prop(available_components, "filter",text="Filter")

            # add components
            row = layout.row(align=True)
            op = row.operator(AddComponentOperator.bl_idname, text="Add", icon="ADD")
            op.component_type = available_components.list
            row.enabled = available_components.list != ''

            layout.separator()

            # paste components
            row = layout.row(align=True)
            row.operator(PasteComponentOperator.bl_idname, text="Paste component ("+bpy.context.window_manager.copied_source_component_name+")", icon="PASTEDOWN")
            row.enabled = registry_has_type_infos and context.window_manager.copied_source_object != ''

            layout.separator()

            # upgrate custom props to components
            upgradeable_customProperties = registry.has_type_infos() and do_object_custom_properties_have_missing_metadata(context.object)
            if upgradeable_customProperties:
                row = layout.row(align=True)
                op = row.operator(GenerateComponent_From_custom_property_Operator.bl_idname, text="generate components from custom properties" , icon="LOOP_FORWARDS") 
                layout.separator()


            components_in_object = object.components_meta.components
            #print("components_names", dict(components_bla).keys())

            for component_name in sorted(get_bevy_components(object)) : # sorted by component name, practical
                #print("component_name", component_name)
                if component_name == "components_meta": 
                    continue
                # anything withouth metadata gets skipped, we only want to see real components, not all custom props
                component_meta =  next(filter(lambda component: component["long_name"] == component_name, components_in_object), None)
                if component_meta == None: 
                    continue
                
                component_invalid = getattr(component_meta, "invalid")
                invalid_details = getattr(component_meta, "invalid_details")
                component_visible = getattr(component_meta, "visible")
                single_field = False

                # our whole row 
                box = layout.box() 
                row = box.row(align=True)
                # "header"
                row.alert = component_invalid
                row.prop(component_meta, "enabled", text="")
                row.label(text=component_name)

                # we fetch the matching ui property group
                root_propertyGroup_name =  registry.get_propertyGroupName_from_longName(component_name)
                """print("root_propertyGroup_name", root_propertyGroup_name)"""
                print("component_meta", component_meta, component_invalid)

                if root_propertyGroup_name:
                    propertyGroup = getattr(component_meta, root_propertyGroup_name, None)
                    """print("propertyGroup", propertyGroup)"""
                    if propertyGroup:
                        # if the component has only 0 or 1 field names, display inline, otherwise change layout
                        single_field = len(propertyGroup.field_names) < 2
                        prop_group_location = box.row(align=True).column()
                        """if single_field:
                            prop_group_location = row.column(align=True)#.split(factor=0.9)#layout.row(align=False)"""
                        
                        if component_visible:
                            if component_invalid:
                                error_message = invalid_details if component_invalid else "Missing component UI data, please reload registry !"
                                prop_group_location.label(text=error_message)
                            draw_propertyGroup(propertyGroup, prop_group_location, [root_propertyGroup_name], component_name)
                        else :
                            row.label(text="details hidden, click on toggle to display")
                    else:
                        error_message = invalid_details if component_invalid else "Missing component UI data, please reload registry !"
                        row.label(text=error_message)

                # "footer" with additional controls
                if component_invalid:
                    if root_propertyGroup_name:
                        propertyGroup = getattr(component_meta, root_propertyGroup_name, None)
                        if propertyGroup:
                            unit_struct = len(propertyGroup.field_names) == 0
                            if unit_struct: 
                                op = row.operator(Fix_Component_Operator.bl_idname, text="", icon="SHADERFX")
                                op.component_name = component_name
                                row.separator()

                op = row.operator(RemoveComponentOperator.bl_idname, text="", icon="X")
                op.component_name = component_name
                row.separator()
                
                op = row.operator(CopyComponentOperator.bl_idname, text="", icon="COPYDOWN")
                op.source_component_name = component_name
                op.source_object_name = object.name
                row.separator()
                
                #if not single_field:
                toggle_icon = "TRIA_DOWN" if component_visible else "TRIA_RIGHT"
                op = row.operator(Toggle_ComponentVisibility.bl_idname, text="", icon=toggle_icon)
                op.component_name = component_name
                #row.separator()

        else: 
            layout.label(text ="Select an object to edit its components")      
