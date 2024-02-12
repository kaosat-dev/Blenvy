
import random


def component_values_shuffler(seed=1, propertyGroup=None, definition=None, registry=None):
    random.seed(seed)

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


    for fieldName in propertyGroup.field_names:
        fieldValue = random.random() # see https://docs.python.org/3/library/random.html
        setattr(propertyGroup , fieldName, fieldValue)
        