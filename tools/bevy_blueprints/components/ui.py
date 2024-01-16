import bpy
import json
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty)
from bpy_types import (PropertyGroup)
from bpy.types import (CollectionProperty)
from .definitions import ComponentDefinition

# FIXME: not sure, hard coded exclude list, feels wrong
exclude = ['Parent', 'Children']

# this one is for UI only, and its inner list contains a useable list of shortnames of components
class ComponentDefinitionsList(bpy.types.PropertyGroup):
    def add_component_to_ui_list(self, context):
        items = []
        wm = context.window_manager
        for index, item in enumerate(wm.component_definitions.values()):
            if self.filter in item.name:
                if not 'Handle' in item.name and item.name not in exclude: # FIXME: hard coded, seems wrong
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


bpy.testcomponents = {}
def dynamic_properties_ui():
    registry = bpy.context.window_manager.components_registry.raw_registry
    registry = json.loads(registry)

    blender_property_mapping = {
        "bool": BoolProperty,

        "u8": IntProperty,
        "u16":IntProperty,
        "u32":IntProperty,
        "u64":IntProperty,
        "u128":IntProperty,
        "u64": IntProperty,

        "i8": IntProperty,
        "i16":IntProperty,
        "i32":IntProperty,
        "i64":IntProperty,
        "i128":IntProperty,

        "f32": FloatProperty,
        "f64": FloatProperty,

        "glam::Vec3": FloatVectorProperty,
        "glam::Vec2": FloatVectorProperty,
        "bevy_render::color::Color": FloatVectorProperty,

        "char": StringProperty,
        "str": StringProperty,
        "alloc::string::String": StringProperty,

        "enum":EnumProperty
    }


    value_types_defaults = {
        "string":" ",
        "boolean": True,
        "float": 0.0,
        "uint": 0,
        "int":0,

        # todo : we are re-doing the work of the bevy /rust side here, but it seems more pratical to alway look for the same field name on the blender side for matches
        "bool": True,

        "u8": 0,
        "u16":0,
        "u32":0,
        "u64":0,
        "u128":0,

        "i8": 0,
        "i16":0,
        "i32":0,
        "i64":0,
        "i128":0,

        "f32": 0.0,
        "f64":0.0,

        "char": " ",
        "str": " ",
        "alloc::string::String": " ",

        "glam::Vec2": [0.0,0.0,0.0],#[0.0, 0.0],
        "glam::Vec3": [0.0, 0.0, 0.0],
        "glam::Vec4": [0.0, 0.0, 0.0, 0.0], 
        "bevy_render::color::Color": [1.0, 1.0, 0.0]#[1.0, 1.0, 0.0, 1.0]
    }

    

    for component_name in registry:
        definition = registry[component_name]
        is_component = definition['isComponent']  if "isComponent" in definition else False
        is_resource = definition['is_resource']  if "is_resource" in definition else False

        short_name = definition["short_name"]
        type_info = definition["typeInfo"] if "typeInfo" in definition else None
        type_def = definition["type"] if "type" in definition else None
        properties = definition["properties"] if "properties" in definition else {}
        prefixItems = definition["prefixItems"] if "prefixItems" in definition else []

        has_properties = len(properties.keys()) > 0
        has_prefixItems = len(prefixItems) > 0
        is_enum = type_info == "Enum"

        if is_component and type_info != "Value" and type_info != "List" and "bevy_bevy_blender_editor_basic_example" in component_name:
            print("entry", component_name, type_def, type_info)# definition)

            __annotations__ = {
            }

            field_names = []
            single_item = True# single item is default, for tupple structs with single types, or structs with no params,
            tupple_or_struct = None
          
            if has_properties:
                tupple_or_struct = "struct"
                default_values = {}
                for property_name in properties.keys():
                    ref_name = properties[property_name]["type"]["$ref"].replace("#/$defs/", "")
                    #print("ref_name", ref_name, "property_name", property_name)
    
                    if ref_name in registry:
                        original = registry[ref_name]
                        original_type_name = original["title"]
                        is_value_type = original_type_name in value_types_defaults
                        value = value_types_defaults[original_type_name] if is_value_type else None
                        default_values[property_name] = value
                        print("ORIGINAL PROP for", property_name, original)

                        if is_value_type and original_type_name in blender_property_mapping:
                            blender_property = blender_property_mapping[original_type_name](name = property_name, default=value)
                            __annotations__[property_name] = blender_property
                            field_names.append(property_name)

                    # if there are sub fields, add an attribute "sub_fields" possibly a pointer property ? or add a standard field to the type , that is stored under "attributes" and not __annotations (better)
                if len(default_values.keys()) > 1:
                    single_item = False

            if has_prefixItems:
                tupple_or_struct = "tupple"

                default_values = []
                prefix_infos = []
                for index, item in enumerate(prefixItems):
                    ref_name = item["type"]["$ref"].replace("#/$defs/", "")
                    if ref_name in registry:
                        original = registry[ref_name]
                        original_type_name = original["title"]
                        is_value_type = original_type_name in value_types_defaults

                        value = value_types_defaults[original_type_name] if is_value_type else None
                        default_values.append(value)
                        prefix_infos.append(original)
                        print("ORIGINAL PROP", original)

                        property_name = str(index)# we cheat a bit, property names are numbers here, as we do not have a real property name
                        if is_value_type and original_type_name in blender_property_mapping:
                            blender_property = blender_property_mapping[original_type_name](name = property_name, default=value)
                            if original_type_name == "bevy_render::color::Color":
                                blender_property = blender_property_mapping[original_type_name](name = property_name, default=value, subtype='COLOR')
                                #FloatVectorProperty()
                                # TODO: use FloatVectorProperty(size= xxx) to define the dimensions of the property

                            __annotations__[property_name] = blender_property
                            field_names.append(property_name)

                if len(default_values) == 1:
                    default_value = default_values[0]
                    infos = prefix_infos[0]
                    type_def = original["title"]
                    print("tupple with a single value", default_value, type_def)
                else: 
                    single_item = False

            if is_enum:
                print("ENUM")
                values = definition["oneOf"]
                if type_def == "object":
                    print("OBBJKEEECT")
                    single_item = False
                else:
                    items = tuple((e, e, "") for e in values)
                    property_name = "0"
                    blender_property = blender_property_mapping["enum"](name = property_name, items=items)
                    __annotations__[property_name] = blender_property
                    field_names.append(property_name)

            print("DONE: __annotations__", __annotations__)
            print("")
            property_group_name = short_name+"_ui"
            # print("creating property group", property_group_name)
            property_group_class = type(property_group_name, (PropertyGroup,), { '__annotations__': __annotations__, 'single_item': single_item, 'field_names': field_names, 'tupple_or_struct':tupple_or_struct })
            
            bpy.utils.register_class(property_group_class)
            setattr(bpy.types.Object, short_name, PointerProperty(type=property_group_class))
            bpy.testcomponents[short_name] = property_group_class


