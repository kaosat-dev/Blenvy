from bpy.props import (StringProperty)
from . import process_component

def process_structs(registry, definition, properties, update, nesting): 
    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos
    short_name = definition["short_name"]

    __annotations__ = {}
    default_values = {}

    nesting = nesting + [short_name]
    print("nesting", nesting)
    print("processing struct", short_name)


    for property_name in properties.keys():
        ref_name = properties[property_name]["type"]["$ref"].replace("#/$defs/", "")

        if ref_name in type_infos:
            original = type_infos[ref_name]
            original_type_name = original["title"]
            is_value_type = original_type_name in value_types_defaults
            value = value_types_defaults[original_type_name] if is_value_type else None
            default_values[property_name] = value

            if is_value_type:
                if original_type_name in blender_property_mapping:
                    blender_property_def = blender_property_mapping[original_type_name]
                    blender_property = blender_property_def["type"](
                        **blender_property_def["presets"],# we inject presets first
                        name = property_name,
                        default = value,
                        update = update
                    )
                    __annotations__[property_name] = blender_property
            else:
                print("NESTING")
                print("NOT A VALUE TYPE", original)
                original_long_name = original["title"]
                (sub_component_group, _) = process_component.process_component(registry, original, update, {"nested": True, "type_name": original_long_name}, nesting)
                # TODO: use lookup in registry, add it if necessary, or retrieve it if it already exists
                __annotations__[property_name] = sub_component_group
        # if there are sub fields, add an attribute "sub_fields" possibly a pointer property ? or add a standard field to the type , that is stored under "attributes" and not __annotations (better)
        else:
            # component not found in type_infos, generating placeholder
            __annotations__[property_name] = StringProperty(default="N/A")
            registry.add_missing_typeInfo(ref_name)
            # the root component also becomes invalid (in practice it is not always a component, but good enough)
            registry.add_invalid_component(nesting[0])

    return __annotations__
