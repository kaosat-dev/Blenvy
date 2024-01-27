from . import process_tupples
from . import process_structs
from bpy.props import (StringProperty)

def process_enum(registry, definition, update, nesting):
    blender_property_mapping = registry.blender_property_mapping
    short_name = definition["short_name"]
    type_def = definition["type"] if "type" in definition else None
    values = definition["oneOf"]

    nesting = nesting+ [short_name]
    __annotations__ = {}
    original_type_name = "enum"

    if type_def == "object":
        labels = []
        additional_annotations = {}
        for item in values:
            item_name = item["title"]
            labels.append(item_name)
            if "prefixItems" in item:
                additional_annotations = additional_annotations | process_tupples.process_tupples(registry, definition, item["prefixItems"], update, "variant_"+item_name, nesting)
            elif "properties" in item:
                additional_annotations = additional_annotations | process_structs.process_structs(registry, definition, item["properties"], update, nesting)
            else: # for the cases where it's neither a tupple nor a structs: FIXME: not 100% sure of this
                annotations = {"variant_"+item_name: StringProperty(default="")}
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
