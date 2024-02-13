
import random
import string
from bpy_types import PropertyGroup


def rand_int():
    return random.randint(0, 100)

def rand_float():
    return random.random()

def random_word(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def random_vec(length, type,):
    value = []
    for i in [0..length]:
        if type == 'float':
            value.append(rand_float())
        if type == 'int':
            value.append(rand_int())
    return value

type_mappings = {
    "bool": lambda value: True if value == "true" else False,

    "u8": rand_int,
    "u16": rand_int,
    "u32": rand_int,
    "u64": rand_int,
    "u128": rand_int,
    "u64": rand_int,
    "usize": rand_int,

    "i8": rand_int,
    "i16": rand_int,
    "i32": rand_int,
    "i64": rand_int,
    "i128": rand_int,

    'f32': rand_float,
    'f64': rand_float,

    "glam::Vec2": lambda : random_vec(2, 'float'),
    "glam::DVec2": lambda : random_vec(2, 'float'),
    "glam::UVec2": lambda : random_vec(2, 'int'),

    'glam::Vec3': lambda : random_vec(3, 'float'),
    "glam::Vec3A": lambda : random_vec(3, 'float'),
    "glam::UVec3": lambda : random_vec(3, 'int'),

    "glam::Vec4": lambda : random_vec(4, 'float'),
    "glam::DVec4": lambda : random_vec(4, 'float'),
    "glam::UVec4": lambda : random_vec(4, 'int'),

    "glam::Quat": lambda : random_vec(4, 'float'),

    'bevy_render::color::Color': lambda : random_vec(4, 'float'),
    'alloc::string::String': lambda : random_word(8),
}

#    
    


def component_values_shuffler(seed=1, property_group=None, definition=None, registry=None, parent=None):
    if parent == None:
        random.seed(seed)

    value_types_defaults = registry.value_types_defaults
    component_name = definition["short_name"]
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

    if is_value_type:
        fieldValue = type_mappings[type_name]() # see https://docs.python.org/3/library/random.html
        return fieldValue #setattr(propertyGroup , fieldName, fieldValue)

    elif type_info == "Struct":
        for index, field_name in enumerate(property_group.field_names):
            item_type_name = definition["properties"][field_name]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition != None:
                value = component_values_shuffler(seed, child_property_group, item_definition, registry, parent=component_name)
            else:
                value = '""'
            print("setting attr", field_name , "for", component_name, "to", value)
            setattr(property_group , field_name, value)

    elif type_info == "Tuple": 
        values = {}
        for index, field_name in enumerate(property_group.field_names):
            item_type_name = definition["prefixItems"][index]["type"]["$ref"].replace("#/$defs/", "")
            item_definition = registry.type_infos[item_type_name] if item_type_name in registry.type_infos else None

            value = getattr(property_group, field_name)
            is_property_group = isinstance(value, PropertyGroup)
            child_property_group = value if is_property_group else None
            if item_definition != None:
                value = component_values_shuffler(seed, child_property_group, item_definition, registry, parent=component_name)
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
                value = component_values_shuffler(seed, child_property_group, item_definition, registry, parent=component_name)
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
                
                value = component_values_shuffler(seed, child_property_group, variant_definition, registry, parent=component_name)
                value = selected + str(value,) 
            elif "properties" in variant_definition:
                value = getattr(property_group, variant_name)
                is_property_group = isinstance(value, PropertyGroup)
                child_property_group = value if is_property_group else None

                value = component_values_shuffler(seed, child_property_group, variant_definition, registry, parent=component_name)
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
                item_value = component_values_shuffler(seed, item, definition, registry, parent=component_name)
                if item_type_name.startswith("wrapper_"): #if we have a "fake" tupple for aka for value types, we need to remove one nested level
                    item_value = item_value[0]
            else:
                item_value = '""'
            value.append(item_value) 
    else:
        value = "" #conversion_tables[type_name](value) if is_value_type else value
    
   
                        