import json
from bpy_types import UIList

class GENERIC_UL_List(UIList): 
    """Generic UIList.""" 

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE' # Make sure your code supports all 3 layout types 
        print("draw item", data, "item", item, "active_data", active_data, "active_propname", active_propname)
        print("sdf", data.field_names, "item", item.field_names)
        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            #print("compact")
            #layout.label(text=getattr(data,"type_name_short")) 
            draw_propertyGroup(item, layout, [], "")

            #layout.prop(item, "name", text="")
            pass
            #propertyGroup = getattr(object, item.component_name+"_ui")

        elif self.layout_type in {'GRID'}: 
            print("grid")
            layout.alignment = 'CENTER' 
            layout.label(text="", icon = custom_icon)
   
def draw_propertyGroup( propertyGroup, layout, nesting =[], rootName=None):
    is_enum = getattr(propertyGroup, "with_enum")
    is_list = getattr(propertyGroup, "with_list") 
    #current_short_name = getattr(propertyGroup, "short_name", "") + "_ui"
    #nesting = nesting + [current_short_name] # we need this convoluted "nested path strings " workaround so that operators working on a given
    # item in our components hierarchy can get the correct propertyGroup by STRINGS because of course, we cannot pass objects to operators...sigh

    # if it is an enum, the first field name is always the list of enum variants, the others are the variants
    field_names = propertyGroup.field_names
    # print("drawing", is_list, propertyGroup, nesting, "component_name", rootName)
    #type_name = getattr(propertyGroup, "type_name", None)#propertyGroup.type_name if "type_name" in propertyGroup else ""
    #print("type name", type_name)
    #print("name", propertyGroup.name, "name2", getattr(propertyGroup, "name"), "short_name", getattr(propertyGroup, "short_name", None), "nesting", nesting)
    if is_enum:
        subrow = layout.row()
        display_name = field_names[0] if propertyGroup.tupple_or_struct == "struct" else ""
        subrow.prop(propertyGroup, field_names[0], text=display_name)
        subrow.separator()
        selection = getattr(propertyGroup, field_names[0])

        for fname in field_names[1:]:
            if fname == "variant_" + selection:
                subrow = layout.row()
                display_name = fname if propertyGroup.tupple_or_struct == "struct" else ""

                nestedPropertyGroup = getattr(propertyGroup, fname)
                nested = getattr(nestedPropertyGroup, "nested", False)
                if not nested:
                    subrow.prop(propertyGroup, fname, text=display_name)
                    subrow.separator()
                else:
                    #print("deal with sub fields", nestedPropertyGroup.field_names)
                    for subfname in nestedPropertyGroup.field_names:
                        subrow = layout.row()
                        display_name = subfname if nestedPropertyGroup.tupple_or_struct == "struct" else ""
                        subrow.prop(nestedPropertyGroup, subfname, text=display_name)
                        subrow.separator()
    elif is_list:
        #print("show list", propertyGroup, dict(propertyGroup), propertyGroup.type_name)
        item_list = getattr(propertyGroup, "list")
        item_type = getattr(propertyGroup, "type_name_short")
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

        #list_column.template_list("GENERIC_UL_List", "The_List", propertyGroup, "list", propertyGroup, "list_index")

    else: 
        for fname in field_names:
            subrow = layout.row()
            nestedPropertyGroup = getattr(propertyGroup, fname)
            nested = getattr(nestedPropertyGroup, "nested", False)
            display_name = fname if propertyGroup.tupple_or_struct == "struct" else ""

            if nested:
                layout.separator()
                layout.label(text=display_name) #  this is the name of the field/sub field
                layout.separator()
                draw_propertyGroup(nestedPropertyGroup, layout.row(), nesting + [fname], rootName )
            else:
                subrow.prop(propertyGroup, fname, text=display_name)
                subrow.separator()
