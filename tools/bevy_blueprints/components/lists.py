import json
from bpy_types import Operator, UIList
from bpy.props import (StringProperty, EnumProperty, PointerProperty, FloatVectorProperty)

class GENERIC_UL_List(UIList): 
    """Demo UIList.""" 
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE' # Make sure your code supports all 3 layout types 
        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            #print("compact")
            #layout.label(text=item.name, icon = custom_icon) 
            #layout.prop(item, "name", text="")
            pass
            #propertyGroup = getattr(object, item.component_name+"_ui")

        elif self.layout_type in {'GRID'}: 
            print("grid")
            layout.alignment = 'CENTER' 
            layout.label(text="", icon = custom_icon)

            


class Generic_LIST_OT_AddItem(Operator): 
    """Add a new item to the list.""" 
    bl_idname = "generic_list.add_item" 
    bl_label = "Add a new item" 


    property_group_path: StringProperty(
        name="property group path",
        description="",
    )
    def execute(self, context): 
        print("")
        propertyGroup = context.object
        for path_item in json.loads(self.property_group_path):
            propertyGroup = getattr(propertyGroup, path_item)

        print("list container", propertyGroup, dict(propertyGroup))
        target_list = getattr(propertyGroup, "list")
        index = getattr(propertyGroup, "list_index")
        item = target_list.add()
        propertyGroup.list_index = index + 1 # we use this to force the change detection

        print("added item", item, item.field_names, getattr(item, "field_names"))
        print("")
        return{'FINISHED'}
    

class Generic_LIST_OT_RemoveItem(Operator): 
    """Remove an item to the list.""" 
    bl_idname = "generic_list.remove_item" 
    bl_label = "Remove a new item" 


    property_group_path: StringProperty(
        name="property group path",
        description="",
    )

    
    def execute(self, context): 
        print("remove from list", context.object)

        propertyGroup = context.object
        for path_item in json.loads(self.property_group_path):
            propertyGroup = getattr(propertyGroup, path_item)

        target_list = getattr(propertyGroup, "list")
        index = getattr(propertyGroup, "list_index")
        target_list.remove(index)
        propertyGroup.list_index = min(max(0, index - 1), len(target_list) - 1) 
        return{'FINISHED'}

