import json
from bpy_types import PropertyGroup


conversion_tables = {
    "glam::Vec3": lambda value: "Vec3(x:"+str(value[0])+ ", y:"+str(value[1])+ ", z:"+str(value[2])+")",
    "glam::Vec2": lambda value: "Vec2(x:"+str(value[0])+ ", y:"+str(value[1])+")",
    "bevy_render::color::Color": lambda value: "Rgba(red:"+str(value[0])+ ", green:"+str(value[1])+ ", blue:"+str(value[2])+ ", alpha:"+str(value[3])+   ")",
    #"bevy_render::color::Color": lambda value: "Color::rgba("+"".join(lambda x: str(x))(value)+")",

}

# helper function for property_group_value_to_custom_property_value 
def compute_values(property_group, registry, parent):
    values = {}
    for field_name in property_group.field_names:
        value = getattr(property_group,field_name)

        # special handling for nested property groups
        is_property_group = isinstance(value, PropertyGroup) 
        if is_property_group:
            prop_group_name = getattr(value, "type_name")
            sub_definition = registry.type_infos[prop_group_name]
            value = property_group_value_to_custom_property_value(value, sub_definition, registry, parent)
        try:
            value = value[:]# in case it is one of the Blender internal array types
        except Exception:
            pass

        values[field_name] = value
    return values

#converts the value of a property group(no matter its complexity) into a single custom property value
# this is more or less a glorified "to_ron()" method (not quite but close to)
def property_group_value_to_custom_property_value(property_group, definition, registry, parent=None):
    component_name = definition["short_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None
    value = None
    print("computing custom property", component_name, type_info, type_def)

    if type_info == "Struct":
        print("is struct", parent)
        #print("STRUCT", property_group.field_names)
        values = compute_values(property_group, registry, "Some") 
        vals = {}
        for key, val in values.items():
            value = val
            #prop_group_name = getattr(val, "type_name")
            #sub_definition = registry.type_infos[prop_group_name]
            # check for type of it AND if it is not enum or so ?
            """  if type(value) == str: 
                value = '"'+value+'"'"""
            vals[key] = value
            
        value = vals
        if len(values) ==0:
            return ''
    elif type_info == "Tuple": 
        values = compute_values(property_group, registry, "Some")  
        value = tuple(e for e in list(values.values()))
    elif type_info == "TupleStruct":
        print("is tupplestruct")
        values = compute_values(property_group, registry, "Some")
        if len(values.keys()) == 1:
            first_key = list(values.keys())[0]
            value = values[first_key]
            #conversion_tables
            sub_type = definition["prefixItems"][0]["type"]["$ref"].replace("#/$defs/", "")
            print("sub _type", sub_type, "value", value)
            if sub_type in conversion_tables:
                value =  conversion_tables[sub_type](value)

            elif type(value) == str:
                value = '"'+value+'"'
        else:
            value = tuple(e for e in list(values.values()))
        print("rertert", type(value))
          
        print("making it into a tupple")
        #if parent == None:
        value = tuple([value])
    elif type_info == "Enum":
        values = compute_values(property_group, registry, "Some")
        if type_def == "object":
            first_key = list(values.keys())[0]
            variant_name = values[first_key]
            value = values.get("variant_" + variant_name, None) # default to None if there is no match, for example for entries withouth Bool/Int/String etc properties, ie empty ones
            # TODO might be worth doing differently
            if value != None:
                is_property_group = isinstance(value, PropertyGroup)
                if is_property_group:
                    prop_group_name = getattr(value, "type_name")
                    sub_definition = registry.type_infos[prop_group_name]
                    value = property_group_value_to_custom_property_value(value, sub_definition, registry, "Some")
                value = variant_name+"("+ str(value) +")"
            else :
                value = variant_name
        else:
            first_key = list(values.keys())[0]
            value = values[first_key]
    elif type_info == "List":
        print("is list")
        item_list = getattr(property_group, "list")
        item_type = getattr(property_group, "type_name_short")
        value = []
        for item in item_list:
            item_type_name = getattr(item, "type_name")
            definition = registry.type_infos[item_type_name]
            item_value = property_group_value_to_custom_property_value(item, definition, registry, "Some")
            print("item type", item_type_name, item_value)
            if item_type_name.startswith("wrapper_"):
                item_value = item_value[0]
            value.append(item_value)
        #TODO if we have a "fake" tupple for aka for value types, we need to remove one nested level somehow ?
    
    else:
        print("OTHR")
        values = compute_values(property_group, registry, "Some")
        if len(values.keys()) == 0:
            value = ''

    print("VALUE", value, type(value))

    #print("generating custom property value", value, type(value))
    if parent == None:
        print("NO PARENT")
        value = str(value).replace("'",  "")
        value = value.replace(",)",")")
        value = value.replace("{", "(").replace("}", ")")
        value = value.replace("True", "true").replace("False", "false")
    return value


def json_to_psuedo_ron(value):
    value = str(value)
    value = value.replace("{", "(").replace("}", ")")
    value = value.replace("'", "") # FIXME: not good ! we do not want to replace string quotes !
    value = value.replace("True", "true").replace("False", "false")
    value = value.replace('"', "")
    return  value


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
