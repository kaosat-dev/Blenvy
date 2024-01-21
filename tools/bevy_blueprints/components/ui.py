import functools
import bpy
import json
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty, CollectionProperty)
from bpy_types import (PropertyGroup)

# FIXME: not sure, hard coded exclude list, feels wrong
exclude = ['Parent', 'Children']

# this one is for UI only, and its inner list contains a useable list of shortnames of components
class ComponentDefinitionsList(bpy.types.PropertyGroup):
    def add_component_to_ui_list(self, context):
        #print("add components to ui_list")
        items = []
        type_infos = context.window_manager.components_registry.type_infos
        short_names = context.window_manager.components_registry.short_names_to_long_names
        for short_name in sorted(short_names.keys()):
            long_name = short_names[short_name]
            definition = type_infos[long_name]
            is_component = definition['isComponent']  if "isComponent" in definition else False

            if self.filter in short_name and is_component:
                if not 'Handle' in short_name and not "Cow" in short_name and not "AssetId" in short_name and short_name not in exclude: # FIXME: hard coded, seems wrong
                    items.append((long_name, short_name, long_name))
        return items

    @classmethod
    def register(cls):
        bpy.types.WindowManager.components_list = bpy.props.PointerProperty(type=ComponentDefinitionsList)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.components_list

    list : bpy.props.EnumProperty(
        name="list",
        description="list",
        # items argument required to initialize, just filled with empty values
        items = add_component_to_ui_list,
    )
    filter: StringProperty(
        name="component filter",
        description="filter for the components list",
        options={'TEXTEDIT_UPDATE'}
    )


class ClearComponentDefinitionsList(bpy.types.Operator):
    ''' clear list of bpy.context.collection.component_definitions '''
    bl_label = "clear component definitions"
    bl_idname = "components.clear_component_definitions"

    def execute(self, context):
        # create a new item, assign its properties
        bpy.context.collection.component_definitions.clear()
        
        return {'FINISHED'}
    


# helper function that returns a lambda, used for the PropertyGroups update function
def update_calback_helper(definition, update, component_name_override):
    return lambda self, context: update(self, context, definition, component_name_override)

def process_properties(registry, definition, properties, update, component_name_override): 
    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos
    short_name = definition["short_name"]

    __annotations__ = {}
    default_values = {}

    for property_name in properties.keys():
        ref_name = properties[property_name]["type"]["$ref"].replace("#/$defs/", "")
        #print("ref_name", ref_name, "property_name", property_name)

        if ref_name in type_infos:
            original = type_infos[ref_name]
            original_type_name = original["title"]
            is_value_type = original_type_name in value_types_defaults
            value = value_types_defaults[original_type_name] if is_value_type else None
            default_values[property_name] = value
            #print("ORIGINAL PROP for", property_name, original)

            if is_value_type:
                if original_type_name in blender_property_mapping:
                    blender_property_def = blender_property_mapping[original_type_name]

                    blender_property = blender_property_def["type"](
                        **blender_property_def["presets"],# we inject presets first
                        name = property_name,
                        default=value,
                        update= update_calback_helper(definition, update, component_name_override)
                        #(lambda property_name, original_type_name: lambda self, context: update(self, context, property_name, definition, original_type_name))(property_name, original_type_name)
                    )
                    __annotations__[property_name] = blender_property
            else:
                print("NESTING")
                print("NOT A VALUE TYPE", original)
                original_long_name = original["title"]
                (sub_component_group, _) = process_component(registry, original, update, {"nested": True, "type_name": original_long_name}, component_name_override=short_name)
                # TODO: use lookup in registry, add it if necessary, or retrieve it if it already exists
                __annotations__[property_name] = sub_component_group
        # if there are sub fields, add an attribute "sub_fields" possibly a pointer property ? or add a standard field to the type , that is stored under "attributes" and not __annotations (better)
        else: 
            print("component not found in type_infos, generating placeholder")
            __annotations__[property_name] = StringProperty(default="N/A")

    if len(default_values.keys()) > 1:
        single_item = False
    return __annotations__

def process_prefixItems(registry, definition, prefixItems, update, name_override=None, component_name_override=None):
    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos
    short_name = definition["short_name"]

    __annotations__ = {}
    tupple_or_struct = "tupple"
    print("YOLO", short_name)

    default_values = []
    prefix_infos = []
    for index, item in enumerate(prefixItems):
        ref_name = item["type"]["$ref"].replace("#/$defs/", "")

        property_name = str(index)# we cheat a bit, property names are numbers here, as we do not have a real property name
        if name_override != None:
            property_name = name_override

        if ref_name in type_infos:
            original = type_infos[ref_name]
            original_type_name = original["title"]
            is_value_type = original_type_name in value_types_defaults

            value = value_types_defaults[original_type_name] if is_value_type else None
            default_values.append(value)
            prefix_infos.append(original)
            #print("ORIGINAL PROP", original)


            if is_value_type:
                if original_type_name in blender_property_mapping:
                    blender_property_def = blender_property_mapping[original_type_name]

                    print("HERE", short_name, original)
                    blender_property = blender_property_def["type"](
                        **blender_property_def["presets"],# we inject presets first
                        name = property_name, 
                        default=value,
                        update= update_calback_helper(definition, update, component_name_override)
                    )
                  
                    __annotations__[property_name] = blender_property
            else:
                print("NESTING")
                print("NOT A VALUE TYPE", original)
                original_long_name = original["title"]
                (sub_component_group, _) = process_component(registry, original, update, {"nested": True, "type_name": original_long_name}, component_name_override=short_name)
                # TODO: use lookup in registry, add it if necessary, or retrieve it if it already exists
                __annotations__[property_name] = sub_component_group

        else: 
            print("component not found in type_infos, generating placeholder")
            __annotations__[property_name] = StringProperty(default="N/A")
    print("annotations", __annotations__)
    return __annotations__


def process_enum(registry, definition, update, component_name_override):
    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos

    short_name = definition["short_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None
    values = definition["oneOf"]

    __annotations__ = {}
    original_type_name = "enum"

    conditiona_fields = {}

    if type_def == "object":
        labels = []
        additional_annotations = {}
        for item in values:
            #print("item", item)
            # TODO: refactor & reuse the rest of our code above 
            item_name = item["title"]
            labels.append(item_name)
            if "prefixItems" in item:
                additional_annotations = additional_annotations | process_prefixItems(registry, definition, item["prefixItems"], update, "variant_"+item_name, component_name_override)
            if "properties" in item:
                print("YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            """if not "prefixItems" in item and not "properties" in item:
                key = "variant_"+item_name
                additional_annotations = {}
                additional_annotations[key] = StringProperty(default="") # TODO replace with empty ??"""

        items = tuple((e, e, e) for e in labels)
        property_name = short_name

        blender_property_def = blender_property_mapping[original_type_name]
        blender_property = blender_property_def["type"](
            **blender_property_def["presets"],# we inject presets first
            name = property_name,
            items=items,
            update= lambda self, context: update(self, context, definition, component_name_override)
)
        __annotations__[property_name] = blender_property

        for a in additional_annotations:
            __annotations__[a] = additional_annotations[a]
        
        # enum_value => what field to display
        # TODO: add a second field + property for the "content" of the enum : already done above, move them around

    else:
        items = tuple((e, e, "") for e in values)
        property_name = short_name
        
        blender_property_def = blender_property_mapping[original_type_name]
        blender_property = blender_property_def["type"](
            **blender_property_def["presets"],# we inject presets first
            name = property_name,
            items=items,
            update=lambda self, context: update(self, context, definition, component_name_override)
        )
        __annotations__[property_name] = blender_property
    
    return __annotations__

def process_list(registry, definition, update, component_name_override=None):
    print("WE GOT A LIST", definition)

    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos

    short_name = definition["short_name"]

    ref_name = definition["items"]["type"]["$ref"].replace("#/$defs/", "")
    print("item type", ref_name)
    original = type_infos[ref_name]

    original_long_name = original["title"]
    (list_content_group, list_content_group_class) = process_component(registry, original, update, {"nested": True, "type_name": original_long_name}, component_name_override=short_name)
    item_collection = CollectionProperty(type=list_content_group_class)
    __annotations__ = {
        'list': item_collection,
        'list_index': IntProperty(name = "Index for my_list", default = 0),
        'item': list_content_group
    }
    return __annotations__

def process_component(registry, definition, update, extras=None, component_name_override=None):
    component_name = definition['title']
    short_name = definition["short_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None
    properties = definition["properties"] if "properties" in definition else {}
    prefixItems = definition["prefixItems"] if "prefixItems" in definition else []

    has_properties = len(properties.keys()) > 0
    has_prefixItems = len(prefixItems) > 0
    is_enum = type_info == "Enum"
    is_list = type_info == "List"

    print("processing", short_name, "component_name_override", component_name_override)

    __annotations__ = {}
    tupple_or_struct = None

    with_properties = False
    with_items = False
    with_enum = False
    with_list = False

    print("entry", component_name, type_def, type_info)# definition)

    if has_properties:
        __annotations__ = __annotations__ | process_properties(registry, definition, properties, update, component_name_override)
        with_properties = True
        tupple_or_struct = "struct"

    if has_prefixItems:
        __annotations__ = __annotations__ | process_prefixItems(registry, definition, prefixItems, update, None, component_name_override)
        with_items = True
        tupple_or_struct = "tupple"

    if is_enum:
        __annotations__ = __annotations__ | process_enum(registry, definition, update, component_name_override)
        with_enum = True

    if is_list:
        __annotations__ = __annotations__ | process_list(registry, definition, update, component_name_override)
        with_list= True

    field_names = []
    for a in __annotations__:
        field_names.append(a)
    single_item = len(field_names)

    extras = extras if extras is not None else {}

    print("DONE: __annotations__", __annotations__)
    print("")
    property_group_name = short_name+"_ui"
    property_group_params = {
         **extras,
        '__annotations__': __annotations__,
        'tupple_or_struct': tupple_or_struct,
        'single_item': single_item, 
        'field_names': field_names, 
        **dict(with_properties = with_properties, with_items= with_items, with_enum= with_enum, with_list= with_list),
       
    }
    (property_group_pointer, property_group_class) = property_group_from_infos(property_group_name, property_group_params)
    registry.register_component_ui(property_group_name, property_group_pointer)
    

    # for practicality, we add an entry for a reverse lookup (short => long name, since we already have long_name => short_name with the keys of the raw registry)
    registry.add_shortName_to_longName(short_name, component_name)

    return (property_group_pointer, property_group_class)
                
def property_group_from_infos(property_group_name, property_group_parameters):
    # print("creating property group", property_group_name)
    property_group_class = type(property_group_name, (PropertyGroup,), property_group_parameters)
    
    bpy.utils.register_class(property_group_class)
    property_group_pointer = PointerProperty(type=property_group_class)
    setattr(bpy.types.Object, property_group_name, property_group_pointer)
    
    return (property_group_pointer, property_group_class)

#converts the value of a property group(no matter its complexity) into a single custom property value
def property_group_value_to_custom_property_value(property_group, definition, registry):
    component_name = definition["short_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None

    value = None
    values = {}
    for field_name in property_group.field_names:
        #print("field name", field_name)
        value = getattr(property_group,field_name)

        # special handling for nested property groups
        is_property_group = isinstance(value, PropertyGroup)
        if is_property_group:
            print("nesting struct")
            prop_group_name = getattr(value, "type_name")
            sub_definition = registry.type_infos[prop_group_name]
            value = property_group_value_to_custom_property_value(value, sub_definition, registry)
            print("sub struct value", value)


        try:
            value = value[:]# in case it is one of the Blender internal array types
        except Exception:
            pass
        print("field name", field_name, "value", value)
        values[field_name] = value

    print("computing custom property", component_name, type_info, type_def)
    # now compute the compound values
    if type_info == "Struct":
        value = values        
    if type_info == "TupleStruct":
        if len(values.keys()) == 1:
            first_key = list(values.keys())[0]
            value = values[first_key]
        else:
            value = str(tuple(e for e in list(values.values())))
    if type_info == "Enum":
        if type_def == "object":
            first_key = list(values.keys())[0]
            selected_entry = values[first_key]
            print("selected entry", selected_entry, values, value)
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
            #selected_entry["title"]+"("+ str(value) +")"

    if len(values.keys()) == 0:
        value = ''
    return value


#converts the value of a single custom property into a value (values) of a property group 
def property_group_value_from_custom_property_value(property_group, definition, registry, custom_property_value):
    print("setting property group value", property_group, definition, custom_property_value)
    type_infos = registry.type_infos
    try: # FIXME this is not normal , the values should be strings !
        custom_property_value = custom_property_value.to_dict()
    except Exception:
        pass
    #parsed_raw_fields = json.loads(custom_property_value)
    # TODO: add disabling of property_group => custom property update call temporarly

    def parse_field(item, property_group, definition):
        type_info = definition["typeInfo"] if "typeInfo" in definition else None
        type_def = definition["type"] if "type" in definition else None
       
        print("parsing", item, "type infos", type_info, "type_def", type_def)
        if isinstance(item, dict):
            for field_name in item:
                #print("field name", field_name)
                field_value = item[field_name]
                # sub field
                if isinstance(getattr(property_group, field_name), PropertyGroup):
                    sub_prop_group = getattr(property_group, field_name)
                    #print("this one is a complex field", field_name, item[field_name])
                    sub_definition = definition["properties"][field_name]
                    parse_field(item[field_name], sub_prop_group, sub_definition)
                   
                else:
                    setattr(property_group, field_name, field_value)
        else:
            print("no dict")
            ref_name = type_def["$ref"].replace("#/$defs/", "")
            original = type_infos[ref_name]
            print("original", original)
            type_info = original["typeInfo"] if "typeInfo" in original else None
            type_def = original["type"] if "type" in original else None

            if type_info == "Enum":
                print("enum")
                if type_def == "string":
                    setattr(property_group, '0', item)
                elif type_def == "object":
                    # TODO: use the same parsing logic as above: ie
                    # - fetch the correct variant definition
                    # - build up the fields from there
                    print("field names", property_group.field_names)
                    property_name = property_group.field_names[0]
                    variants_real_names = list(map(lambda name: name.replace("variant_", ""), property_group.field_names))
                    print("property_name", property_name, variants_real_names)
                    chosen_variant_raw = item.split("(") # FIXME: not reliable, use some more robust logic
                    chosen_variant = chosen_variant_raw[0]
                    chosen_variant_value = chosen_variant_raw[2].replace("))", "")
                    print("chosen variant", chosen_variant, "value", chosen_variant_value)

                    setattr(property_group, property_name, chosen_variant)
                    print("definition", definition)

                    #setattr(property_group, variant_name, valo)
            else: 
                setattr(property_group, '0', item) 
    print('parsed_raw_fields', custom_property_value)
    parse_field(custom_property_value, property_group, definition)
   

def dynamic_properties_ui():
    registry = bpy.context.window_manager.components_registry
    if registry.type_infos == None:
        registry.load_type_infos()

    type_infos = registry.type_infos

    def update_component(self, context, definition, component_name_override=None):
        current_object = bpy.context.object
        update_disabled = current_object["__disable__update"] if "__disable__update" in current_object else False
        if update_disabled:
            return

        component_name = definition["short_name"]
        print("update in component", self, component_name, component_name_override)#, type_def, type_info,self,self.name , "context",context.object.name, "attribute name", field_name)
        if component_name_override != None:
            component_name = component_name_override
            long_name = registry.short_names_to_long_names.get(component_name)
            definition = registry.type_infos[long_name]
            short_name = definition["short_name"]
            # self = registry.component_uis[short_name+"_ui"]
            self = getattr(current_object, component_name+"_ui") # FIXME: yikes, I REALLY dislike this ! using the context out of left field
            # then again, trying to use the data from registry.component_uis does not seem to work

            print("using override", component_name)
        # we use our helper to set the values
        print("self", self)
        context.object[component_name] = property_group_value_to_custom_property_value(self, definition, registry)

    for component_name in type_infos:
        definition = type_infos[component_name]
        process_component(registry, definition, update_component)


        """
        object[component_definition.name] = 0.5
        property_manager = object.id_properties_ui(component_definition.name)
        property_manager.update(min=-10, max=10, soft_min=-5, soft_max=5)

        print("property_manager", property_manager)

        object[component_definition.name] = [0.8,0.2,1.0]
        property_manager = object.id_properties_ui(component_definition.name)
        property_manager.update(subtype='COLOR')

        #IDPropertyUIManager
        #rna_ui = object[component_definition.name].get('_RNA_UI')
        """