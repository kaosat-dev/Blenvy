import json
from bpy_types import PropertyGroup

# helper function for property_group_value_to_custom_property_value 
def compute_values(property_group, registry):
    values = {}
    print("compute bla", property_group)
    for field_name in property_group.field_names:
        value = getattr(property_group,field_name)
        # special handling for nested property groups
        is_property_group = isinstance(value, PropertyGroup) 
        if is_property_group:
            prop_group_name = getattr(value, "type_name")
            sub_definition = registry.type_infos[prop_group_name]
            value = property_group_value_to_custom_property_value(value, sub_definition, registry)
        try:
            value = value[:]# in case it is one of the Blender internal array types
        except Exception:
            pass
        values[field_name] = value
    return values

#converts the value of a property group(no matter its complexity) into a single custom property value
# this is more or less a glorified "to_string()" method (not quite but close to)
def property_group_value_to_custom_property_value(property_group, definition, registry):
    component_name = definition["short_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None

    value = None
    print("computing custom property", component_name, type_info, type_def)
    print("property_group", property_group, "definition", definition)

    if type_info == "Struct":
        value = compute_values(property_group, registry)       
    elif type_info == "Tuple": 
        values = compute_values(property_group, registry)  
        value = tuple(e for e in list(values.values()))
    elif type_info == "TupleStruct":
        values = compute_values(property_group, registry)
        if len(values.keys()) == 1:
            first_key = list(values.keys())[0]
            value = values[first_key]
        else:
            value = str(tuple(e for e in list(values.values())))
    elif type_info == "Enum":
        values = compute_values(property_group, registry)
        if type_def == "object":
            first_key = list(values.keys())[0]
            selected_entry = values[first_key]
            value = values.get("variant_" + selected_entry, None) # default to None if there is no match, for example for entries withouth Bool/Int/String etc properties, ie empty ones
            # TODO might be worth doing differently
            if value != None:
                is_property_group = isinstance(value, PropertyGroup)
                if is_property_group:
                    print("nesting")
                    prop_group_name = getattr(value, "type_name")
                    sub_definition = registry.type_infos[prop_group_name]
                    value = property_group_value_to_custom_property_value(value, sub_definition, registry)
                value = selected_entry+"("+ str(value) +")"
            else :
                value = selected_entry
        else:
            first_key = list(values.keys())[0]
            value = values[first_key]
    elif type_info == "List":
        item_list = getattr(property_group, "list")
        item_type = getattr(property_group, "type_name_short")
        value = []
        for item in item_list:
            item_type_name = getattr(item, "type_name")
            definition = registry.type_infos[item_type_name]
            item_value = property_group_value_to_custom_property_value(item, definition, registry)
            value.append(item_value)
        value = str(value)
    
    else:
        values = compute_values(property_group, registry)
        if len(values.keys()) == 0:
            value = ''

    print("generating custom property value", value, type(value))
    return str(value) # not sure about this casting

import re
#converts the value of a single custom property into a value (values) of a property group 
def property_group_value_from_custom_property_value(property_group, definition, registry, custom_property_value):
    print(" ")
    print("setting property group value", property_group, definition, custom_property_value)
    type_infos = registry.type_infos
    value_types_defaults = registry.value_types_defaults

    try: # FIXME this is not normal , the values should be strings !
        custom_property_value = custom_property_value.to_dict()
    except Exception:
        pass

    def parse_field(item, property_group, definition, field_name):
        type_info = definition["typeInfo"] if "typeInfo" in definition else None
        type_def = definition["type"] if "type" in definition else None
        properties = definition["properties"] if "properties" in definition else {}
        prefixItems = definition["prefixItems"] if "prefixItems" in definition else []
        has_properties = len(properties.keys()) > 0
        has_prefixItems = len(prefixItems) > 0
        is_enum = type_info == "Enum"
        is_list = type_info == "List"
        is_value_type = type_def in value_types_defaults

        # print("parsing field", item, "type infos", type_info, "type_def", type_def)
        if has_properties:
            for field_name in property_group.field_names:
                # sub field
                if isinstance(getattr(property_group, field_name), PropertyGroup):
                    sub_prop_group = getattr(property_group, field_name)
                    ref_name = properties[field_name]["type"]["$ref"].replace("#/$defs/", "")
                    sub_definition = type_infos[ref_name]
                    parse_field(item[field_name], sub_prop_group, sub_definition, field_name)
                else:
                    setattr(property_group, field_name, item[field_name])
        if has_prefixItems:
            if len(property_group.field_names) == 1:
                setattr(property_group, "0", item) # FIXME: not ideal
            else:
                for field_name in property_group.field_names:
                    setattr(property_group, field_name, item)
        if is_enum:
            if type_def == "object":
                regexp = re.search('(^[^\(]+)(\((.*)\))', item)
                chosen_variant = regexp.group(1)
                chosen_variant_value = regexp.group(3).replace("'", '"').replace("(", "[").replace(")","]")
                chosen_variant_value = json.loads(chosen_variant_value)

                # first set chosen selection
                field_name = property_group.field_names[0]
                setattr(property_group, field_name, chosen_variant)
                
                # thenlook for the information about the matching variant
                sub_definition= None
                for variant in definition["oneOf"]:
                    if variant["title"] == chosen_variant:
                        ref_name = variant["prefixItems"][0]["type"]["$ref"].replace("#/$defs/", "")
                        sub_definition = type_infos[ref_name]
                        break
                variant_name = "variant_"+chosen_variant 
                if isinstance(getattr(property_group, variant_name), PropertyGroup):
                    sub_prop_group = getattr(property_group, variant_name)
                    parse_field(chosen_variant_value, sub_prop_group, sub_definition, variant_name)
                else: 
                    setattr(property_group, variant_name, chosen_variant_value)
            else:
                field_name = property_group.field_names[0]
                setattr(property_group, field_name, item)

        if is_list:
            pass

        if is_value_type:
            pass
            
    # print('parsed_raw_fields', custom_property_value)
    try:
        parse_field(custom_property_value, property_group, definition, None)
    except Exception as error:
        print("failed to parse raw custom property data", error)
