import bpy
import json
from bpy.props import (StringProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty)
from bpy_types import (PropertyGroup)
from bpy.types import (CollectionProperty)
from .definitions import ComponentDefinition


# this one is for UI only, and its inner list contains a useable list of shortnames of components
class ComponentDefinitionsList(bpy.types.PropertyGroup):

    def update(self, v):
        print("updating filter", v)

    def add_component_to_ui_list(self, context):
        items = []
        wm = context.window_manager
        for index, item in enumerate(wm.component_definitions.values()):
            if self.filter in item.name:
                items.append((str(index), item.name, item.long_name))
        return items

    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_list = bpy.props.PointerProperty(type=ComponentDefinitionsList)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.components_list

    list : bpy.props.EnumProperty(
        name="list",
        description="list",
        # items argument required to initialize, just filled with empty values
        items = add_component_to_ui_list,
    )
    filter: StringProperty(
        name="component filter",
        description="filter for the components list",
        update = update,
        options={'TEXTEDIT_UPDATE'}
    )


class ClearComponentDefinitionsList(bpy.types.Operator):
    ''' clear list of bpy.context.collection.component_definitions '''
    bl_label = "clear component definitions"
    bl_idname = "components.clear_component_definitions"

    def execute(self, context):
        # create a new item, assign its properties
        bpy.context.collection.component_definitions.clear()
        
        return {'FINISHED'}
    

bpy.samplePropertyGroups = {}

def generate_enum_properties():
    print("generate_enum_properties")
    for component_definition in bpy.context.window_manager.component_definitions:
        # FIXME: horrible, use registry instead of bpy.context.window_manager.component_definitions
        data = json.loads(component_definition.data)
        real_type = data["type_info"]
        values = data["values"]
        # print("component definition", component_definition.name, component_definition.type_name, real_type, values)
        if real_type == "Enum":
            items = tuple((e, e, "") for e in values)
            type_name = "enum_"+component_definition.name
          
            #enumClass = type(type_name, (bpy.types.EnumProperty,), attributes)
            groupName = type_name
            attributes = {
            }
            attributes["enum"] = EnumProperty(
                items=items,
                name="enum"
            )

            attributes["yikes"] = StringProperty(
                name="yikes",
                description="foo"
            )

            propertyGroupClass = type(groupName, (PropertyGroup,), { '__annotations__': attributes })
            # register our custom propertyGroup
            bpy.utils.register_class(propertyGroupClass)
            # add it to the needed type
            setattr(bpy.types.Object, type_name, PointerProperty(type=propertyGroupClass))
            bpy.samplePropertyGroups[type_name] = propertyGroupClass

def unregister_stuff():
    try:
        for key, value in bpy.samplePropertyGroups.items():
            delattr(bpy.types.Object, key)
            bpy.utils.unregister_class(value)
    except Exception:#UnboundLocalError:
        pass
