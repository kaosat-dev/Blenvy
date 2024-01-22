from bpy_types import Operator, UIList
from bpy.props import (StringProperty, EnumProperty, PointerProperty, FloatVectorProperty)

class GENERIC_UL_List(UIList): 
    """Demo UIList.""" 
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE' # Make sure your code supports all 3 layout types 
        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            print("compact")
            #layout.label(text=item.name, icon = custom_icon) 
            layout.prop(item, "name", text="")

            #propertyGroup = getattr(object, item.component_name+"_ui")

        elif self.layout_type in {'GRID'}: 
            print("grid")
            layout.alignment = 'CENTER' 
            layout.label(text="", icon = custom_icon)

            


class Generic_LIST_OT_AddItem(Operator): 
    """Add a new item to the list.""" 
    bl_idname = "generic_list.add_item" 
    bl_label = "Add a new item" 


    property_group_name: StringProperty(
        name="property group name",
        description="",
    )

    def execute(self, context): 

        print("add to list", context.object, self.property_group_name)
        #context.scene.my_list.add() 
        my_list_container = getattr(context.object, self.property_group_name)
        my_list = getattr(my_list_container, "list")
        print("my list", my_list)
        item = my_list.add()
        item.name = ""
        item.component_name = "foo"
        print("added item", item.field_names)
        return{'FINISHED'}
    

class Generic_LIST_OT_RemoveItem(Operator): 
    """Remove an item to the list.""" 
    bl_idname = "generic_list.remove_item" 
    bl_label = "Remove a new item" 


    property_group_name: StringProperty(
        name="property group name",
        description="",
    )

    def execute(self, context): 
        print("remove from list", context.object, self.property_group_name)
       
        return{'FINISHED'}
    
    def execute(self, context): 
        print("remove from list", context.object, self.property_group_name)

        my_list_container = getattr(context.object, self.property_group_name)
        my_list = getattr(my_list_container, "list")
        index = getattr(my_list_container, "list_index")
        my_list.remove(index)
        my_list_container.list_index = min(max(0, index - 1), len(my_list) - 1) 
        return{'FINISHED'}

