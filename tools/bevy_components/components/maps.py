import json
from bpy_types import Operator, UIList
from bpy.props import (StringProperty, EnumProperty, PointerProperty, FloatVectorProperty, IntProperty)

class GENERIC_MAP_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "generic_map.map_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER', 'UNDO'}

    action: EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""))) # type: ignore
    
    property_group_path: StringProperty(
        name="property group path",
        description="",
    ) # type: ignore

    component_name: StringProperty(
        name="component name",
        description="",
    ) # type: ignore

    def invoke(self, context, event):
        object = context.object
        # information is stored in component meta
        components_in_object = object.components_meta.components
        component_meta =  next(filter(lambda component: component["long_name"] == self.component_name, components_in_object), None)

        propertyGroup = component_meta
        for path_item in json.loads(self.property_group_path):
            propertyGroup = getattr(propertyGroup, path_item)

        target_list = getattr(propertyGroup, "list")
        index = getattr(propertyGroup, "list_index")

        values_list = getattr(propertyGroup, "values_list")
        values_index = getattr(propertyGroup, "values_list_index")


        if self.action == 'DOWN' and index < len(target_list) - 1:
            #item_next = scn.rule_list[index + 1].name
            target_list.move(index, index + 1)
            propertyGroup.list_index += 1
        
        elif self.action == 'UP' and index >= 1:
            #item_prev = scn.rule_list[index - 1].name
            target_list.move(index, index - 1)
            propertyGroup.list_index -= 1

        elif self.action == 'REMOVE':
            target_list.remove(index)
            propertyGroup.list_index = min(max(0, index - 1), len(target_list) - 1) 

        if self.action == 'ADD':
            key = target_list.add()
            value = values_list.add()
            
            propertyGroup.list_index = index + 1 # we use this to force the change detection
            propertyGroup.values_index = index + 1 # we use this to force the change detection


            #info = '"%s" added to list' % (item.name)
            #self.report({'INFO'}, info)

        return {"FINISHED"}