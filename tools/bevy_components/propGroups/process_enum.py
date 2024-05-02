from bpy.props import (StringProperty)
from . import process_component

def process_enum(registry, definition, update, nesting, nesting_long_names):
    blender_property_mapping = registry.blender_property_mapping
    short_name = definition["short_name"]
    long_name = definition["title"]

    type_def = definition["type"] if "type" in definition else None
    values = definition["oneOf"]

    nesting = nesting + [short_name]
    nesting_long_names = nesting_long_names = [long_name]

    __annotations__ = {}
    original_type_name = "enum"

    #print("processing enum", short_name, definition)

    if type_def == "object":
        labels = []
        additional_annotations = {}
        for item in values:
            item_name = item["title"]
            item_short_name = item["short_name"] if "short_name" in item else item_name
            variant_name = "variant_"+item_short_name
            labels.append(item_name)

            if "prefixItems" in item:
                #print("tupple variant in enum", short_name, item)
                registry.add_custom_type(item_short_name, item)
                (sub_component_group, _) = process_component.process_component(registry, item, update, {"nested": True}, nesting, nesting_long_names) 
                additional_annotations[variant_name] = sub_component_group
            elif "properties" in item:
                #print("struct variant in enum", short_name, item)
                registry.add_custom_type(item_short_name, item)
                (sub_component_group, _) = process_component.process_component(registry, item, update, {"nested": True}, nesting, nesting_long_names) 
                additional_annotations[variant_name] = sub_component_group
            else: # for the cases where it's neither a tupple nor a structs: FIXME: not 100% sure of this
                #print("other variant in enum", short_name)
                annotations = {"variant_"+item_name: StringProperty(default="----<ignore_field>----")}
                additional_annotations = additional_annotations | annotations

        items = tuple((e, e, e) for e in labels)
        property_name = short_name

        blender_property_def = blender_property_mapping[original_type_name]
        blender_property = blender_property_def["type"](
            **blender_property_def["presets"],# we inject presets first
            name = property_name,
            items=items,
            update= update
)
        __annotations__[property_name] = blender_property

        for a in additional_annotations:
            __annotations__[a] = additional_annotations[a]
        # enum_value => what field to display
        # a second field + property for the "content" of the enum
    else:
        items = tuple((e, e, "") for e in values)
        property_name = short_name
        
        blender_property_def = blender_property_mapping[original_type_name]
        blender_property = blender_property_def["type"](
            **blender_property_def["presets"],# we inject presets first
            name = property_name,
            items=items,
            update= update
        )
        __annotations__[property_name] = blender_property
    
    return __annotations__
