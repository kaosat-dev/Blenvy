from bpy.props import (StringProperty, IntProperty, CollectionProperty)
from .utils import generate_wrapper_propertyGroup
from . import process_component

def process_list(registry, definition, update, nesting=[], nesting_long_names=[]):
    value_types_defaults = registry.value_types_defaults 
    type_infos = registry.type_infos

    short_name = definition["short_name"]
    long_name = definition["title"]
    ref_name = definition["items"]["type"]["$ref"].replace("#/$defs/", "")
    
    item_definition = type_infos[ref_name]
    item_long_name = item_definition["title"]
    item_short_name = item_definition["short_name"]
    is_item_value_type = item_long_name in value_types_defaults

    property_group_class = None
    #if the content of the list is a unit type, we need to generate a fake wrapper, otherwise we cannot use layout.prop(group, "propertyName") as there is no propertyName !
    if is_item_value_type:
        property_group_class = generate_wrapper_propertyGroup(short_name, item_long_name, definition["items"]["type"]["$ref"],registry, update)
    else:
        (_, list_content_group_class) = process_component.process_component(registry, item_definition, update, {"nested": True, "type_name": item_long_name}, nesting)
        property_group_class = list_content_group_class

    nesting = nesting+[short_name]
    nesting_long_names = nesting_long_names + [long_name]

    item_collection = CollectionProperty(type=property_group_class)

    item_short_name = item_short_name if not is_item_value_type else  "wrapper_" + item_short_name
    __annotations__ = {
        "list": item_collection,
        "list_index": IntProperty(name = "Index for list", default = 0,  update=update),
        "type_name_short": StringProperty(default=item_short_name)
    }

    return __annotations__