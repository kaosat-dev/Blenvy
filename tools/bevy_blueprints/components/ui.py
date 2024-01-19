import functools
import bpy
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty)
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
def update_calback_helper(property_name, original_type_name, definition, update):
    return lambda self, context: update(self, context, property_name, definition, original_type_name)

def process_properties(registry, definition, properties, update): 
    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos

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
                        update= update_calback_helper(property_name, original_type_name, definition, update)
                        #(lambda property_name, original_type_name: lambda self, context: update(self, context, property_name, definition, original_type_name))(property_name, original_type_name)
                    )
                    __annotations__[property_name] = blender_property
            else:
                print("NOT A VALUE TYPE", original)
                # FIXME: this is not right
                #__annotations__ = __annotations__ | process_component(registry, original, update)
        # if there are sub fields, add an attribute "sub_fields" possibly a pointer property ? or add a standard field to the type , that is stored under "attributes" and not __annotations (better)
        else: 
            print("component not found in type_infos, generating placeholder")
            __annotations__[property_name] = StringProperty(default="N/A")

    if len(default_values.keys()) > 1:
        single_item = False
    return __annotations__

def process_prefixItems(registry, definition, prefixItems, update, name_override=None):
    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos
    short_name = definition["short_name"]

    __annotations__ = {}
    tupple_or_struct = "tupple"
    print("YOLO")

    default_values = []
    prefix_infos = []
    for index, item in enumerate(prefixItems):
        ref_name = item["type"]["$ref"].replace("#/$defs/", "")
        if ref_name in type_infos:
            original = type_infos[ref_name]
            original_type_name = original["title"]
            is_value_type = original_type_name in value_types_defaults

            value = value_types_defaults[original_type_name] if is_value_type else None
            default_values.append(value)
            prefix_infos.append(original)
            #print("ORIGINAL PROP", original)

            property_name = str(index)# we cheat a bit, property names are numbers here, as we do not have a real property name
            if name_override != None:
                property_name = name_override
            if is_value_type:
                if original_type_name in blender_property_mapping:
                    blender_property_def = blender_property_mapping[original_type_name]

                    print("HERE", short_name, original)
                    blender_property = blender_property_def["type"](
                        **blender_property_def["presets"],# we inject presets first
                        name = property_name, 
                        default=value,
                        update= update_calback_helper(property_name, original_type_name, definition, update)
                    )
                  
                    __annotations__[property_name] = blender_property
            else:
                print("NOT A VALUE TYPE", original)
        else: 
            print("component not found in type_infos, generating placeholder")
            #__annotations__[property_name] = None

    if len(default_values) == 1:
        default_value = default_values[0]
        infos = prefix_infos[0]
        type_def = original["title"]
        #print("tupple with a single value", default_value, type_def)
    else: 
        single_item = False
    return __annotations__


def process_enum(registry, definition, update):
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
                additional_annotations = additional_annotations | process_prefixItems(registry, definition, item["prefixItems"], update, "variant_"+item_name)

        items = tuple((e, e, e) for e in labels)
        property_name = short_name


        def update_enum(self, context, property_name, definition, original_type):
            print("update enum")
            update(self, context, property_name, definition, original_type)

        blender_property_def = blender_property_mapping[original_type_name]
        blender_property = blender_property_def["type"](
            **blender_property_def["presets"],# we inject presets first
            name = property_name,
            items=items,
            update= lambda self, context: update_enum(self, context, property_name, definition, "enum")
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
            update=lambda self, context: update(self, context, property_name, definition, "enum")
        )
        __annotations__[property_name] = blender_property
    
    return __annotations__

def process_component(registry, definition, update):
    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos

    component_name = definition['title']
    is_component = definition['isComponent']  if "isComponent" in definition else False
    is_resource = definition['is_resource']  if "is_resource" in definition else False

    short_name = definition["short_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None
    properties = definition["properties"] if "properties" in definition else {}
    prefixItems = definition["prefixItems"] if "prefixItems" in definition else []

    has_properties = len(properties.keys()) > 0
    has_prefixItems = len(prefixItems) > 0
    is_enum = type_info == "Enum"

    __annotations__ = {}

    if is_component and type_info != "Value" and type_info != "List" :
        print("entry", component_name, type_def, type_info)# definition)

        if has_properties:
            tupple_or_struct = "struct"
            __annotations__ = __annotations__ | process_properties(registry, definition, properties, update)

        if has_prefixItems:
            tupple_or_struct = "tupple"
            __annotations__ = __annotations__ | process_prefixItems(registry, definition, prefixItems, update)

        if is_enum:
            __annotations__ = __annotations__ | process_enum(registry, definition, update)
    return __annotations__
                

def property_group_from_infos(property_group_name, annotations, tupple_or_struct, extras):
    field_names = []
    for a in annotations:
        field_names.append(a)
    single_item = len(field_names)

    property_group_parameters =  { **extras, '__annotations__': annotations, 'single_item': single_item, 'field_names': field_names, 'tupple_or_struct':tupple_or_struct }
    # print("creating property group", property_group_name)
    property_group_class = type(property_group_name, (PropertyGroup,), property_group_parameters)
    
    bpy.utils.register_class(property_group_class)
    setattr(bpy.types.Object, property_group_name, PointerProperty(type=property_group_class))
    
    return property_group_class

#converts the value of a property group(no matter its complexity) into a single custom property value
def property_group_value_to_custom_property_value(property_group, definition):
    component_name = definition["short_name"]
    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type_def = definition["type"] if "type" in definition else None

    value = None
    values = {}
    for field_name in property_group.field_names:
        #print("field name", field_name)
        value = getattr(property_group,field_name)
        try:
            value = value[:]# in case it is one of the Blender internal array types
        except Exception:
            pass
        #print("field name", field_name, "value", value)
        values[field_name] = value

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
            value = values["variant_" + selected_entry]
            value = selected_entry+"("+ str(value) +")"
        else:
            first_key = list(values.keys())[0]
            value = values[first_key]
            #selected_entry["title"]+"("+ str(value) +")"

    if len(values.keys()) == 0:
        value = ''
    return value


#converts the value of a single custom property into a value (values) of a property group 
def property_group_value_from_custom_property_value():
    pass

def dynamic_properties_ui():
    registry = bpy.context.window_manager.components_registry
    if registry.type_infos == None:
        registry.load_type_infos()

    type_infos = registry.type_infos


    def update_component(self, context, field_name, definition, type_name):
        component_name = definition["short_name"]
        print("update in component", self, component_name, type_name, field_name)#, type_def, type_info,self,self.name , "context",context.object.name, "attribute name", field_name)
        # we use our helper to set the values
        context.object[component_name] = property_group_value_to_custom_property_value(self, definition)

    for component_name in type_infos:
        definition = type_infos[component_name]
        is_component = definition['isComponent']  if "isComponent" in definition else False
        is_resource = definition['is_resource']  if "is_resource" in definition else False

        short_name = definition["short_name"]
        type_info = definition["typeInfo"] if "typeInfo" in definition else None
        type_def = definition["type"] if "type" in definition else None
        properties = definition["properties"] if "properties" in definition else {}
        prefixItems = definition["prefixItems"] if "prefixItems" in definition else []

        has_properties = len(properties.keys()) > 0
        has_prefixItems = len(prefixItems) > 0
        is_enum = type_info == "Enum"

        #if is_component and type_info != "Value" and type_info != "List": # and "bevy_bevy_blender_editor_basic_example" in component_name:
        print("entry", component_name, type_def, type_info)# definition)

        __annotations__ = {}
        tupple_or_struct = None
        with_properties = False
        with_items = False
        with_enum = False
        
        if has_properties:
            tupple_or_struct = "struct"
            with_properties = True
            __annotations__ = __annotations__ | process_properties(registry, definition, properties, update_component)
        
        if has_prefixItems:
            tupple_or_struct = "tupple"
            with_properties = True
            __annotations__ = __annotations__ | process_prefixItems(registry, definition, prefixItems, update_component)

        if is_enum:
            with_enum = True
            __annotations__ = __annotations__ | process_enum(registry, definition, update_component)
                
        print("DONE: __annotations__", __annotations__)
        print("")
        property_group_name = short_name+"_ui"

        property_group_class = property_group_from_infos(property_group_name, __annotations__, tupple_or_struct, dict(with_properties = with_properties, with_items= with_items, with_enum= with_enum))
        registry.register_component_ui(property_group_name, property_group_class)
    
        # for practicality, we add an entry for a reverse lookup (short => long name, since we already have long_name => short_name with the keys of the raw registry)
        registry.add_shortName_to_longName(short_name, component_name)



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