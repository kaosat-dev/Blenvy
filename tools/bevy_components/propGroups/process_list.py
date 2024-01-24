from bpy.props import (StringProperty, IntProperty, CollectionProperty)
from .utils import update_calback_helper
from . import process_component

def process_list(registry, definition, update, component_name_override=None, nesting=[]):
    print("WE GOT A LIST", definition)
    #TODO: if the content of the list is a unit type, we need to generate a fake wrapper, otherwise we cannot use layout.prop(group, "propertyName") as there is no propertyName !

    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos

    short_name = definition["short_name"]
    ref_name = definition["items"]["type"]["$ref"].replace("#/$defs/", "")
    original = type_infos[ref_name]
    original_long_name = original["title"]

    nesting = nesting+[short_name]
    print("nesting", nesting)

    (list_content_group, list_content_group_class) = process_component.process_component(registry, original, update, {"nested": True, "type_name": original_long_name}, component_name_override, nesting)
    item_collection = CollectionProperty(type=list_content_group_class)

    __annotations__ = {
        "list": item_collection,
        "list_index": IntProperty(name = "Index for my_list", default = 0,  update=update),#update=update_calback_helper(definition, update, component_name_override)),
        "type_name_short": StringProperty(default=short_name)
    }

    return __annotations__