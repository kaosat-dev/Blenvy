from bpy_types import PropertyGroup
import re
import json


def parse_struct_string(content):
    print("processing stuff", content)
    fields = {}
    buff = []
    current_fieldName = None
    gathering_nested = False
    nesting_level = 0 

    for index, char in enumerate(content):
        buff.append(char)
        if char == "," and not gathering_nested:
            val = "".join(buff[:-1])
            buff = []
            if not current_fieldName in fields:
                fields[current_fieldName] = val.strip()
            print("done with field name", current_fieldName, "value", fields[current_fieldName])

        if char == "(" : #and not gathering_nested:
            print("started gathering nested", current_fieldName)
            gathering_nested = True
            """regexp = re.search('^[^(]*\((.*)\).*', )
            content = regexp.group(1)"""
        if char == ")" :
            val = "".join(buff).strip()
            buff = []
            fields[current_fieldName] = val  # FIXME: stupid to add back parens #parse_struct_string(val)
            print("finished gathering nested", current_fieldName, "value", fields[current_fieldName])

            #print("index", index, len(content) )
            if len(content) - index > 2: #TODO: check this
                print("nested done")
                gathering_nested = False
        if char == ":" and not gathering_nested:
            fieldName = "".join(buff[:-1])
            buff = []
            #fields[fieldName] = ""
            current_fieldName = fieldName.strip()
            print("starting field name", fieldName)
    #print("done with field name", current_fieldName)
    if not gathering_nested:
        val = "".join(buff)
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
        if char == ","and nesting_level == start_nesting:
            end_offset = index
            end_offset = len(string) if end_offset == 0 else end_offset

            val = "".join(string[start_offset:end_offset])
            buff = []
            #if not current_fieldName in fields:
            fields.append(val.strip())
            field_index += 1

            print("start and end offset", start_offset, end_offset, "total length", len(string))
            print("done with field name", field_index, "value", fields)

        if char == "[" or char == "(":
            if nesting_level == start_nesting:
                start_offset = index
                print("start offset", start_offset)
            nesting_level  += 1
            print("nesting down", nesting_level)

        if char == "]" or char == ")" :
            if nesting_level == start_nesting:
                end_offset = index
                print("end offset", end_offset)
            nesting_level  -= 1
            print("nesting up", nesting_level)

       
        if char == ":" and nesting_level == start_nesting:
            buff = []
            print("starting field name", field_index)

    #stop = len(string)- end_offset
    end_offset = len(string) if end_offset == 0 else end_offset
    print("final start and end offset", start_offset, end_offset, "total length", len(string))

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
    "glam::UVec2": lambda value: parse_vec2(value, int, "UVec2"),

    'glam::Vec3': lambda value: parse_vec3(value, float, "Vec3"),
    "glam::Vec3A": lambda value: parse_vec3(value, float, "Vec3A"),
    "glam::UVec3": lambda value: parse_vec3(value, int, "UVec3"),

    "glam::Vec4": lambda value: parse_vec4(value, float, "Vec4"),
    "glam::DVec4": lambda value: parse_vec4(value, float, "DVec4"),
    "glam::UVec4": lambda value: parse_vec4(value, int, "UVec4"),

    "glam::Quat": lambda value: parse_vec4(value, float, "Quat"),

    'alloc::string::String': lambda value: str(value.replace('"', "")),
    'bevy_render::color::Color': lambda value: parse_color(value, float, "Rgba")
}

#converts the value of a single custom property into a value (values) of a property group 
def property_group_value_from_custom_property_value(property_group, definition, registry, value):
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

    print(" ")
    print("raw value", value)
    print("definition", definition)


    if is_value_type:
        print("value type", value, "type name in type_mappings", type_name in type_mappings)
        value = type_mappings[type_name](value) if type_name in type_mappings else value
        print("value", value)
        return value
    elif type_info == "Struct":
        if len(property_group.field_names) != 0 :
            regexp = re.search('^[^(]*\((.*)\).*', value)
            content = regexp.group(1) if value != "" else ""
            print("is struct", content)

            custom_property_values = parse_struct_string(content)
            values = {}
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
                    custom_prop_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_prop_value)
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
        regexp = re.search('^[^(]*\((.*)\).*', value)
        content = regexp.group(1) if value != "" else ""
        custom_property_values = parse_tuplestruct_string(content)#, start_nesting=1)
        print("custom_property_values", custom_property_values)

        for index, field_name in enumerate(property_group.field_names):
            item_type_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None
            
            custom_property_value = custom_property_values[index]

            propGroup_value = getattr(property_group, field_name)
            is_property_group = isinstance(propGroup_value, PropertyGroup)
            child_property_group = propGroup_value if is_property_group else None
            if item_definition != None:
                propGroup_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_property_value)

    elif type_info == "TupleStruct":
        '''regexp = re.search('^[^(]*\((.*)\).*', value)
        content = regexp.group(1)'''

        regexp = re.search('(^[^\(]*)(\((.*)\))', value)
        content = regexp.group(3)

        print("is TupleStruct", value)
        custom_property_values = parse_tuplestruct_string(content)
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
                custom_prop_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_prop_value)
            try:
                setattr(property_group, field_name, custom_prop_value)
            except Exception as error:
                print("could not set property value", error)

    elif type_info == "Enum":
        field_names = property_group.field_names
        print("is Enum", value)
        if type_def == "object":
            regexp = re.search('(^[^\(]+)(\((.*)\))', value)
            chosen_variant_raw = regexp.group(1)
            chosen_variant_value = regexp.group(3)
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
                
                value = property_group_value_from_custom_property_value(child_property_group, variant_definition, registry, value=chosen_variant_value)
                
            elif "properties" in variant_definition:
                value = getattr(property_group, chosen_variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None

                value = property_group_value_from_custom_property_value(child_property_group, variant_definition, registry, value=chosen_variant_value)
                
        else:
            print("other enum")
            chosen_variant_raw = value
            setattr(property_group, field_names[0], chosen_variant_raw)


        
    elif type_info == "List":
        print("is List", value)
        item_list = getattr(property_group, "list")
        print("item_list", item_list)
        custom_property_values = parse_tuplestruct_string(value, start_nesting=1)
        for index, item in enumerate(item_list):
            print("index", index)
            item_type_name = getattr(item, "type_name")
            definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            custom_prop_value = custom_property_values[index]
            print("list item", index, "value", custom_prop_value)

            if definition != None:
                item_value = property_group_value_from_custom_property_value(item, definition, registry, value=custom_prop_value)
                if item_type_name.startswith("wrapper_"): #if we have a "fake" tupple for aka for value types, we need to remove one nested level
                    item_value = item_value[0]
            
    else:
        print("something else")

#converts the value of a single custom property into a value (values) of a property group 
def property_group_value_from_custom_property_value_old(property_group, definition, registry, custom_property_value):
    #print(" ")
    #print("setting property group value", property_group, definition, custom_property_value)
    type_infos = registry.type_infos
    value_types_defaults = registry.value_types_defaults
    print("custom_property_value", custom_property_value)

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

        print("parsing field", item, "type infos", type_info, "type_def", type_def)
        if type_info == "Struct":
            print("is object")
            for field_name in property_group.field_names:
                print("field name", field_name)
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
            print("is list")

        if is_value_type:
            print("is value type")
            
    try:
        parse_field(custom_property_value, property_group, definition, None)
    except Exception as error:
        print("failed to parse raw custom property data", error)
