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
                value = selected + str(value,) #"{}{},".format(selected ,value)
            elif "properties" in variant_definition:
                value = getattr(property_group, variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None

                value = property_group_value_to_custom_property_value(child_property_group, variant_definition, registry, parent=component_name, value=value)
                value = selected + str(value,)
            else:
                value = getattr(property_group, variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None
                if child_property_group:
                    value = property_group_value_to_custom_property_value(child_property_group, variant_definition, registry, parent=component_name, value=value)
                    value = selected + str(value,)
                else:
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
        value = '""' if isinstance(value, PropertyGroup) else value
        
        
    #print("generating custom property value", value, type(value))
    if isinstance(value, str):
        value = value.replace("'", "")

    if parent == None:
        value = str(value).replace("'",  "")
        value = value.replace(",)",")")
        value = value.replace("{", "(").replace("}", ")")
        value = value.replace("True", "true").replace("False", "false")
    return value

