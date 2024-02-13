from decimal import Decimal
from bpy_types import PropertyGroup
import re
import json


def parse_struct_string(string, start_nesting=0):
    print("processing struct string", string, "start_nesting", start_nesting)
    fields = {}
    buff = []
    current_fieldName = None
    nesting_level = 0 

    start_offset = 0
    end_offset = 0

    for index, char in enumerate(string):
        buff.append(char)
        if char == "," and nesting_level == start_nesting:
            #print("first case", end_offset)
            end_offset = index
            end_offset = len(string) if end_offset == 0 else end_offset

            val = "".join(string[start_offset:end_offset])
            fields[current_fieldName] = val.strip()
            start_offset = index + 1
            #print("done with field name", current_fieldName, "value", fields[current_fieldName])

        if char == "(" :
            nesting_level  += 1
            if nesting_level == start_nesting:
                start_offset = index + 1 
                #print("nesting & setting start offset", start_offset)
            #print("nesting down", nesting_level)

        if char == ")":
            #print("nesting up", nesting_level)
            if nesting_level == start_nesting:
                end_offset = index
                #print("unesting & setting end offset", end_offset)
            nesting_level  -= 1


        if char == ":" and nesting_level == start_nesting:
            end_offset = index
            fieldName = "".join(string[start_offset:end_offset])
            current_fieldName = fieldName.strip()
            start_offset = index + 1
            end_offset = 0 #hack
            #print("starting field name", fieldName, "index", index)
            buff = []
            
    end_offset = len(string) if end_offset == 0 else end_offset
    #print("final start and end offset", start_offset, end_offset, "total length", len(string))

    val = "".join(string[start_offset:end_offset])

    fields[current_fieldName] = val.strip()
    print("done with all fields", fields)
    return fields

def parse_tuplestruct_string(string, start_nesting=0):
    print("processing tuppleStruct", string, "start_nesting", start_nesting)
    fields = []
    buff = []
    nesting_level = 0 
    field_index = 0

    start_offset = 0
    end_offset = 0
    # todo: strip all stuff before start_nesting

    for index, char in enumerate(string):
        buff.append(char)
        if char == "," and nesting_level == start_nesting:
            end_offset = index
            end_offset = len(string) if end_offset == 0 else end_offset

            val = "".join(string[start_offset:end_offset])
            fields.append(val.strip())
            field_index += 1
            #print("start and end offset", start_offset, end_offset, "total length", len(string))
            #print("done with field name", field_index, "value", fields)
            start_offset = index + 1
            end_offset = 0 # hack

        if char == "[" or char == "(":
            nesting_level  += 1
            if nesting_level == start_nesting:
                start_offset = index + 1 
                #print("nesting & setting start offset", start_offset)
            #print("nesting down", nesting_level)

        if char == "]" or char == ")" :
            if nesting_level == start_nesting:
                end_offset = index
                #print("unesting & setting end offset", end_offset)
            #print("nesting up", nesting_level)
            nesting_level  -= 1


    end_offset = len(string) if end_offset == 0 else end_offset
    #print("final start and end offset", start_offset, end_offset, "total length", len(string))

    val = "".join(string[start_offset:end_offset]) #if end_offset != 0 else buff)
    fields.append(val.strip())
    print("done with all fields", fields)
    return fields


def parse_vec2(value, caster, typeName):
    parsed = parse_struct_string(value.replace(typeName,"").replace("(", "").replace(")","") )
    return [caster(parsed['x']), caster(parsed['y'])]

def parse_vec3(value, caster, typeName):
    parsed = parse_struct_string(value.replace(typeName,"").replace("(", "").replace(")","") )
    return [caster(parsed['x']), caster(parsed['y']), caster(parsed['z'])]

def parse_vec4(value, caster, typeName):
    parsed = parse_struct_string(value.replace(typeName,"").replace("(", "").replace(")","") )
    return [caster(parsed['x']), caster(parsed['y']), caster(parsed['z']), caster(parsed['w'])]

def parse_color(value, caster, typeName):
    parsed = parse_struct_string(value.replace(typeName,"").replace("(", "").replace(")","") )
    return [caster(parsed['red']), caster(parsed['green']), caster(parsed['blue']), caster(parsed['alpha'])]

def to_int(input):
    return int(float(input))

type_mappings = {
    "bool": lambda value: True if value == "true" else False,

    "u8": lambda value: int(value),
    "u16": lambda value: int(value),
    "u32": lambda value: int(value),
    "u64": lambda value: int(value),
    "u128": lambda value: int(value),
    "u64": lambda value: int(value),
    "usize": lambda value: int(value),

    "i8": lambda value: int(value),
    "i16": lambda value: int(value),
    "i32": lambda value: int(value),
    "i64": lambda value: int(value),
    "i128": lambda value: int(value),

    'f32': lambda value: float(value),
    'f64': lambda value: float(value),

    "glam::Vec2": lambda value: parse_vec2(value, float, "Vec2"),
    "glam::DVec2": lambda value: parse_vec2(value, float, "DVec2"),
    "glam::UVec2": lambda value: parse_vec2(value, to_int, "UVec2"),

    'glam::Vec3': lambda value: parse_vec3(value, float, "Vec3"),
    "glam::Vec3A": lambda value: parse_vec3(value, float, "Vec3A"),
    "glam::UVec3": lambda value: parse_vec3(value, to_int, "UVec3"),

    "glam::Vec4": lambda value: parse_vec4(value, float, "Vec4"),
    "glam::DVec4": lambda value: parse_vec4(value, float, "DVec4"),
    "glam::UVec4": lambda value: parse_vec4(value, to_int, "UVec4"),

    "glam::Quat": lambda value: parse_vec4(value, float, "Quat"),

    'alloc::string::String': lambda value: str(value.replace('"', "")),
    'bevy_render::color::Color': lambda value: parse_color(value, float, "Rgba")
}

#converts the value of a single custom property into a value (values) of a property group 
def property_group_value_from_custom_property_value(property_group, definition, registry, value, nesting = []):
    value_types_defaults = registry.value_types_defaults

    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None
    properties = definition["properties"] if "properties" in definition else {}
    prefixItems = definition["prefixItems"] if "prefixItems" in definition else []
    has_properties = len(properties.keys()) > 0
    has_prefixItems = len(prefixItems) > 0
    is_enum = type_info == "Enum"
    is_list = type_info == "List"
    type_name = definition["title"]

    #is_value_type = type_def in value_types_defaults or type_name in value_types_defaults
    is_value_type = type_name in value_types_defaults
    nesting = nesting + [definition["short_name"]]

    print(" ")
    print("raw value", value, "nesting", nesting)
    print("nesting", len(nesting))
    print("definition", definition)

    

    if is_value_type:
        print("value type", value, "type name in type_mappings", type_name in type_mappings)
        value = value.replace("(", "").replace(")", "")# FIXME: temporary, incoherent use of nesting levels between parse_tuplestruct_string & parse_struct_string
        value = type_mappings[type_name](value) if type_name in type_mappings else value
        print("value", value)
        return value
    elif type_info == "Struct":
        if len(property_group.field_names) != 0 :
            print("is struct", value)
            custom_property_values = parse_struct_string(value, start_nesting=1 if value.startswith("(") else 0)
            print("custom_property_values", custom_property_values)
            for index, field_name in enumerate(property_group.field_names):
                print("FIELD NAME", field_name)
                item_type_name = definition["properties"][field_name]["type"]["$ref"].replace("#/$defs/", "")
                item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

                custom_prop_value = custom_property_values[field_name]
                print("field value", custom_prop_value)

                propGroup_value = getattr(property_group, field_name)
                is_property_group = isinstance(propGroup_value, PropertyGroup)
                child_property_group = propGroup_value if is_property_group else None
                if item_definition != None:
                    custom_prop_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_prop_value, nesting=nesting)
                else:
                    custom_prop_value = custom_prop_value
                try:
                    setattr(property_group, field_name, custom_prop_value) # FIXME: this fails for setting enum property values
                except Exception as error:
                    print("could not set property value", error)

        else:
            print("struct with zero fields")

    elif type_info == "Tuple": 
        print("is Tuple", value)
        custom_property_values = parse_tuplestruct_string(value, start_nesting=1 if len(nesting) == 1 else 1)
        print("custom_property_values", custom_property_values)

        for index, field_name in enumerate(property_group.field_names):
            item_type_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None
            
            custom_property_value = custom_property_values[index]

            propGroup_value = getattr(property_group, field_name)
            is_property_group = isinstance(propGroup_value, PropertyGroup)
            child_property_group = propGroup_value if is_property_group else None
            if item_definition != None:
                propGroup_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_property_value, nesting=nesting)

    elif type_info == "TupleStruct":
        print("is TupleStruct", value)
        custom_property_values = parse_tuplestruct_string(value, start_nesting=1 if len(nesting) == 1 else 0)
        print("custom_property_values", custom_property_values)
        for index, field_name in enumerate(property_group.field_names):
            item_type_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            custom_prop_value = custom_property_values[index]
            print("field name", field_name, "value", custom_prop_value)

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition != None:
                custom_prop_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_prop_value, nesting=nesting)
            try:
                setattr(property_group, field_name, custom_prop_value)
            except Exception as error:
                print("could not set property value", error)

    elif type_info == "Enum":
        field_names = property_group.field_names
        print("is Enum", value)
        if type_def == "object":
            regexp = re.search('(^[^\(]+)(\((.*)\))', value)
            try:
                chosen_variant_raw = regexp.group(1)
                chosen_variant_value = regexp.group(3)
                chosen_variant_name = "variant_" + chosen_variant_raw 
            except:
                chosen_variant_raw = value
                chosen_variant_value = ""
                chosen_variant_name = "variant_" + chosen_variant_raw 
            print("object Enum", value, chosen_variant_raw, "value", chosen_variant_value, property_group.field_names)
            selection_index = property_group.field_names.index(chosen_variant_name)
            variant_definition = definition["oneOf"][selection_index-1]
            print("variant definition", variant_definition)

            # first we set WHAT variant is selected
            setattr(property_group, field_names[0], chosen_variant_raw)

            # and then we set the value of the variant
            if "prefixItems" in variant_definition:
                value = getattr(property_group, chosen_variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None
                
                chosen_variant_value = "(" +chosen_variant_value +")" # needed to handle nesting correctly
                value = property_group_value_from_custom_property_value(child_property_group, variant_definition, registry, value=chosen_variant_value, nesting=nesting)
                
            elif "properties" in variant_definition:
                value = getattr(property_group, chosen_variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None

                value = property_group_value_from_custom_property_value(child_property_group, variant_definition, registry, value=chosen_variant_value, nesting=nesting)
                
        else:
            print("other enum")
            chosen_variant_raw = value
            setattr(property_group, field_names[0], chosen_variant_raw)


        
    elif type_info == "List":
        print("is List", value)
        item_list = getattr(property_group, "list")
        print("item_list", item_list)
        custom_property_values = parse_tuplestruct_string(value, start_nesting=1)
        print("custom_property_values", custom_property_values)
        for index, item in enumerate(item_list):
            print("index", index)
            item_type_name = getattr(item, "type_name")
            definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            custom_prop_value = custom_property_values[index]
            print("list item", index, "value", custom_prop_value)

            if definition != None:
                item_value = property_group_value_from_custom_property_value(item, definition, registry, value=custom_prop_value, nesting=nesting)
                if item_type_name.startswith("wrapper_"): #if we have a "fake" tupple for aka for value types, we need to remove one nested level
                    item_value = item_value[0]
            
    else:
        print("something else")