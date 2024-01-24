import bpy
from bpy.props import (StringProperty, IntProperty, CollectionProperty)
from bpy_types import PropertyGroup
from . import process_component

def process_list(registry, definition, update, nesting=[]):
    print("WE GOT A LIST", definition)
    #TODO: if the content of the list is a unit type, we need to generate a fake wrapper, otherwise we cannot use layout.prop(group, "propertyName") as there is no propertyName !

    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos

    short_name = definition["short_name"]
    ref_name = definition["items"]["type"]["$ref"].replace("#/$defs/", "")
    
    item_definition = type_infos[ref_name]
    item_long_name = item_definition["title"]
    is_item_value_type = item_long_name in value_types_defaults

    print("LIST ITEM DEFINITION", item_definition, "value type", is_item_value_type)
    bla = None
    if is_item_value_type:
        wrapper_name = "wrapper_" + short_name
        print("generating wrapper", wrapper_name, "definition", definition["items"]["type"]["$ref"])

        wrapper_definition = {
            "isComponent": False,
            "isResource": False,
            "items": False,
            "prefixItems": [
                {
                    "type": {
                        "$ref": definition["items"]["type"]["$ref"]
                    }
                }
            ],
            "short_name": wrapper_name,
            "title": wrapper_name,
            "type": "array",
            "typeInfo": "TupleStruct"
        }
        #registry.type_infos[wrapper_name] = wrapper_definition
        #foo = PropertyGroup()
        registry.add_custom_type(wrapper_name, wrapper_definition)

        blender_property = StringProperty(default="", update=update)
        if item_long_name in blender_property_mapping:
            value = value_types_defaults[item_long_name] if is_item_value_type else None
            blender_property_def = blender_property_mapping[item_long_name]
            blender_property = blender_property_def["type"](
                **blender_property_def["presets"],# we inject presets first
                name = "property_name",
                default = value,
                update = update
            )
            
        wrapper_annotations = {
            '0' : blender_property#StringProperty(default="", update=update)
        }
        property_group_params = {
            '__annotations__': wrapper_annotations,
            'tupple_or_struct': "tupple",
            'single_item': True, 
            'field_names': ['0'], 
            **dict(with_properties = False, with_items= True, with_enum= False, with_list= False, short_name= wrapper_name, type_name=wrapper_name),
            #'root_component': root_component
        }
        bla = property_group_class = type(wrapper_name, (PropertyGroup,), property_group_params)
        bpy.utils.register_class(property_group_class)
    else:
        (_, list_content_group_class) = process_component.process_component(registry, item_definition, update, {"nested": True, "type_name": item_long_name}, nesting)
        bla = list_content_group_class

    nesting = nesting+[short_name]
    print("nesting", nesting)

    
    item_collection = CollectionProperty(type=bla)

    __annotations__ = {
        "list": item_collection,
        "list_index": IntProperty(name = "Index for list", default = 0,  update=update),
        "type_name_short": StringProperty(default=short_name)
    }

    return __annotations__