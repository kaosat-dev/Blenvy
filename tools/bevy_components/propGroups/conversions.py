import json
from bpy_types import PropertyGroup


conversion_tables = {
    "bool": lambda value: value,

    "char": lambda value: '"'+value+'"',
    "str": lambda value: '"'+value+'"',
    "alloc::string::String": lambda value: '"'+value+'"',

    "glam::Vec2": lambda value: "Vec2(x:"+str(value[0])+ ", y:"+str(value[1])+")",
    "glam::DVec2": lambda value: "DVec2(x:"+str(value[0])+ ", y:"+str(value[1])+")",
    "glam::UVec2": lambda value: "UVec2(x:"+str(value[0])+ ", y:"+str(value[1])+")",

    "glam::Vec3": lambda value: "Vec3(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+")",
    "glam::Vec3A": lambda value: "Vec3A(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+")",
    "glam::UVec3": lambda value: "UVec3(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+")",

    "glam::Vec4": lambda value: "Vec4(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+ ", w:"+str(value[3])+")",
    "glam::DVec4": lambda value: "DVec4(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+ ", w:"+str(value[3])+")",
    "glam::UVec4": lambda value: "UVec4(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+ ", w:"+str(value[3])+")",

    "glam::Quat":  lambda value: "Quat(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+ ", w:"+str(value[3])+")",

    "bevy_render::color::Color": lambda value: "Rgba(red:"+str(value[0])+ ", green:"+str(value[1])+ ", blue:"+str(value[2])+ ", alpha:"+str(value[3])+   ")",
}

#converts the value of a property group(no matter its complexity) into a single custom property value
# this is more or less a glorified "to_ron()" method (not quite but close to)
def property_group_value_to_custom_property_value(property_group, definition, registry, parent=None, value=None):
    component_name = definition["short_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None
    type_name = definition["title"]
    is_value_type = type_name in conversion_tables
    #print("computing custom property", component_name, type_info, type_def, type_name)

    if is_value_type:
        value = conversion_tables[type_name](value)
    elif type_info == "Struct":
        values = {}
        if len(property_group.field_names) ==0:
            value = ''
        else:
            for index, field_name in enumerate(property_group.field_names):
                item_type_name = definition["properties"][field_name]["type"]["$ref"].replace("#/$defs/", "")
                item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

                value = getattr(property_group, field_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None
                if item_definition != None:
                    value = property_group_value_to_custom_property_value(child_property_group, item_definition, registry, parent=component_name, value=value)
                else:
                    value = '""'
                values[field_name] = value
            value = values        
    elif type_info == "Tuple": 
        values = {}
        for index, field_name in enumerate(property_group.field_names):
            item_type_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition != None:
                value = property_group_value_to_custom_property_value(child_property_group, item_definition, registry, parent=component_name, value=value)
            else:
                value = '""'
            values[field_name] = value
        value = tuple(e for e in list(values.values()))

    elif type_info == "TupleStruct":
        values = {}
        for index, field_name in enumerate(property_group.field_names):
            item_type_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition != None:
                value = property_group_value_to_custom_property_value(child_property_group, item_definition, registry, parent=component_name, value=value)
            else:
                value = '""'
            values[field_name] = value
        
        value = tuple(e for e in list(values.values()))
    elif type_info == "Enum":
        selected = getattr(property_group, component_name)

        if type_def == "object":
            selection_index = property_group.field_names.index("variant_"+selected)
            variant_name = property_group.field_names[selection_index]
            variant_definition = definition["oneOf"][selection_index-1]
            if "prefixItems" in variant_definition:
                value = getattr(property_group, variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None
                
                value = property_group_value_to_custom_property_value(child_property_group, variant_definition, registry, parent=component_name, value=value)
                value = selected + str(value,) 
            elif "properties" in variant_definition:
                value = getattr(property_group, variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None

                value = property_group_value_to_custom_property_value(child_property_group, variant_definition, registry, parent=component_name, value=value)
                value = selected + str(value,)
            else:
                print("basic enum stuff")
                value = selected # here the value of the enum is just the name of the variant
        else: 
            value = selected

    elif type_info == "List":
        item_list = getattr(property_group, "list")
        #item_type = getattr(property_group, "type_name_short")
        value = []
        for item in item_list:
            item_type_name = getattr(item, "type_name")
            definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None
            if definition != None:
                item_value = property_group_value_to_custom_property_value(item, definition, registry, component_name, None)
                if item_type_name.startswith("wrapper_"): #if we have a "fake" tupple for aka for value types, we need to remove one nested level
                    item_value = item_value[0]
            else:
                item_value = '""'
            value.append(item_value) 
    else:
        value = conversion_tables[type_name](value) if is_value_type else value
        
    #print("VALUE", value, type(value))
    #print("generating custom property value", value, type(value))
    if parent == None:
        value = str(value).replace("'",  "")
        value = value.replace(",)",")")
        value = value.replace("{", "(").replace("}", ")")
        value = value.replace("True", "true").replace("False", "false")
    return value

import re

def foo(colon_seperated_string):
    results = {}
    bla = colon_seperated_string.split(",")
    for item in bla:
        [name, value] = item.split(":")
        results[name.strip()] = value.strip()
    return results
        
def parse_struct_string(content):
    print("processing stuff", content)
    fields = {}
    buff = []
    current_fieldName = None
    gathering_nested = False

    for index, char in enumerate(content):
        buff.append(char)
        if char == "," and not gathering_nested:
            #print("done with field name", current_fieldName)
            val = "".join(buff[:-1])
            buff = []
            fields[current_fieldName] = val.strip()
        if char == "(":
            #print("started gathering nested", current_fieldName)
            gathering_nested = True
            """regexp = re.search('^[^(]*\((.*)\).*', )
            content = regexp.group(1)"""
        if char == ")":
            #print("finished gathering nested", current_fieldName)
            val = "".join(buff[1:-1:]).strip()[1:]
            buff = []
            fields[current_fieldName] = "(" + val +")" # FIXME: stupid to add back parens #parse_struct_string(val)
            #print("index", index, len(content) )
            if len(content) - index > 2: #TODO: check this
                gathering_nested = False

        if char == ":" and not gathering_nested:
            fieldName = "".join(buff[:-1])
            buff = []
            #fields[fieldName] = ""
            current_fieldName = fieldName.strip()
            #print("current field name", fieldName)
    #print("done with field name", current_fieldName)
    if not gathering_nested:
        val = "".join(buff)
        fields[current_fieldName] = val.strip()
    return fields


type_mappings = {
    'f32': lambda value: float(value),
    'u64' : lambda value: int(value),
    'alloc::string::String': lambda value: str(value),
    'bevy_render::color::Color': lambda value: [float(parse_struct_string(value)['red']), float(parse_struct_string(value)['green']), float(parse_struct_string(value)['blue']) , float(parse_struct_string(value)['alpha'])] # FIXME: horribly ineficient, nest lambdas
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

    is_value_type = type_def in value_types_defaults or type_name in value_types_defaults

    print("raw value", value, definition)


    if is_value_type:
        print("value type", value, definition)
        value = type_mappings[type_name](value) if type_name in type_mappings else value
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

                value = getattr(property_group, field_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None
                if item_definition != None:
                    custom_prop_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_prop_value)
                else:
                    custom_prop_value = custom_prop_value
                values[field_name] = custom_prop_value
                try:
                    setattr(property_group, field_name, custom_prop_value) # FIXME: this fails for setting enum property values
                except Exception as error:
                    print("could not set property value", error)

            print("VALUES", values)
        else:
            print("struct with zero fields")

    elif type_info == "Tuple": 
        print("is Tuple")
    elif type_info == "TupleStruct":
        regexp = re.search('^[^(]*\((.*)\).*', value)
        content = regexp.group(1)

        regexp = re.search('(^[^\(]+)(\((.*)\))', content)
        content = regexp.group(3)

        print("is TupleStruct", content)
        custom_property_values = content
        print("custom_property_values", custom_property_values)
        for index, field_name in enumerate(property_group.field_names):
            item_type_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            custom_prop_value = custom_property_values
            print("field name", field_name, "value", custom_prop_value)

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition != None:
                custom_prop_value = property_group_value_from_custom_property_value(child_property_group, item_definition, registry, value=custom_prop_value)
            else:
                custom_prop_value = custom_prop_value
            setattr(property_group, field_name, custom_prop_value)


    elif type_info == "Enum":
        regexp = re.search('(^[^\(]+)(\((.*)\))', value)
        chosen_variant = regexp.group(1)
        chosen_variant_value = regexp.group(3)
        chosen_variant_name = "variant_" + chosen_variant 
        print("is Enum", value, chosen_variant, chosen_variant_value, property_group.field_names)
        if type_def == "object":
            print("object enum")
        else:
            setattr(property_group, chosen_variant_name, chosen_variant_value)
    elif type_info == "List":
        print("is List")
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
