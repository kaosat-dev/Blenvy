import functools
import bpy
import json
from bpy.props import (StringProperty, BoolProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, PointerProperty)
from bpy_types import (PropertyGroup)
from bpy.types import (CollectionProperty)
from .definitions import ComponentDefinition

# FIXME: not sure, hard coded exclude list, feels wrong
exclude = ['Parent', 'Children']

# this one is for UI only, and its inner list contains a useable list of shortnames of components
class ComponentDefinitionsList(bpy.types.PropertyGroup):
    def add_component_to_ui_list(self, context):
        items = []
        wm = context.window_manager
        for index, item in enumerate(wm.component_definitions.values()):
            if self.filter in item.name:
                if not 'Handle' in item.name and item.name not in exclude: # FIXME: hard coded, seems wrong
                    items.append((str(index), item.name, item.long_name))
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
    

bpy.samplePropertyGroups = {}

def generate_enum_properties():
    print("generate_enum_properties")
    for component_definition in bpy.context.window_manager.component_definitions:
        # FIXME: horrible, use registry instead of bpy.context.window_manager.component_definitions
        data = json.loads(component_definition.data)
        real_type = data["type_info"]
        values = data["values"]
        # print("component definition", component_definition.name, component_definition.type_name, real_type, values)
        if real_type == "Enum":
            items = tuple((e, e, "") for e in values)
            type_name = "enum_"+component_definition.name
          
            #enumClass = type(type_name, (bpy.types.EnumProperty,), attributes)
            groupName = type_name
            attributes = {
            }
            attributes["enum"] = EnumProperty(
                items=items,
                name="enum"
            )

            propertyGroupClass = type(groupName, (PropertyGroup,), { '__annotations__': attributes })
            # register our custom propertyGroup
            bpy.utils.register_class(propertyGroupClass)
            # add it to the needed type
            setattr(bpy.types.Object, type_name, PointerProperty(type=propertyGroupClass))
            bpy.samplePropertyGroups[type_name] = propertyGroupClass

def unregister_stuff():
    try:
        for key, value in bpy.samplePropertyGroups.items():
            delattr(bpy.types.Object, key)
            bpy.utils.unregister_class(value)
    except Exception:#UnboundLocalError:
        pass

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
            print("ORIGINAL PROP for", property_name, original)

            if is_value_type:
                if original_type_name in blender_property_mapping:
                    blender_property = blender_property_mapping[original_type_name](
                        name = property_name,
                        default=value,
                        #update= functools.partial(update, self, context, property_name, definition, original_type_name)
                        update= lambda self, context: update(self, context, field_name=property_name, definition=definition, type_name=original_type_name)
                    )
                    if original_type_name == "bevy_render::color::Color":
                        blender_property = blender_property_mapping[original_type_name](
                            name = property_name,
                            default=value,
                            subtype='COLOR',
                            update=lambda self, context: update(self, context, property_name, definition, original_type_name)
                        )
                        #FloatVectorProperty()
                        # TODO: use FloatVectorProperty(size= xxx) to define the dimensions of the property
                    __annotations__[property_name] = blender_property
            else:
                print("NOT A VALUE TYPE", original)
                # FIXME: this is not right
                #__annotations__ = __annotations__ | process_component(registry, original, update)
        # if there are sub fields, add an attribute "sub_fields" possibly a pointer property ? or add a standard field to the type , that is stored under "attributes" and not __annotations (better)
    if len(default_values.keys()) > 1:
        single_item = False
    return __annotations__

def process_prefixItems(registry, definition, prefixItems, update):
    value_types_defaults = registry.value_types_defaults 
    blender_property_mapping = registry.blender_property_mapping
    type_infos = registry.type_infos
    short_name = definition["short_name"]

    __annotations__ = {}
    tupple_or_struct = "tupple"

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
            if is_value_type:
                if original_type_name in blender_property_mapping:
                    blender_property = blender_property_mapping[original_type_name](
                        name = property_name, 
                        default=value,
                        update=lambda self, context: update(self, context, property_name, definition, original_type_name)
                    )
                    if original_type_name == "bevy_render::color::Color":
                        blender_property = blender_property_mapping[original_type_name](
                            name = property_name, 
                            default=value, 
                            subtype='COLOR',
                            update=lambda self, context: update(self, context, property_name, definition, original_type_name)
                            )
                        #FloatVectorProperty()
                        # TODO: use FloatVectorProperty(size= xxx) to define the dimensions of the property
                    __annotations__[property_name] = blender_property
            else:
                print("NOT A VALUE TYPE", original)

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

    if type_def == "object":
        labels = []
        additional_annotations = {}
        for item in values:
            #print("item", item)
            # TODO: refactor & reuse the rest of our code above 
            labels.append(item["title"])
            if "prefixItems" in item:
                additional_annotations = additional_annotations | process_prefixItems(registry, definition, item["prefixItems"], update)

        items = tuple((e, e, e) for e in labels)
        property_name = short_name

        blender_property = blender_property_mapping["enum"](
            name = property_name,
            items=items,
            update=lambda self, context: update(self, context, property_name, definition, "enum")
)
        __annotations__[property_name] = blender_property

        for a in additional_annotations:
            __annotations__[a] = additional_annotations[a]
        
        # enum_value => what field to display
        # TODO: add a second field + property for the "content" of the enum : already done above, move them around

        single_item = False
    else:
        items = tuple((e, e, "") for e in values)
        property_name = short_name
        blender_property = blender_property_mapping["enum"](
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
                

def dynamic_properties_ui():
    registry = bpy.context.window_manager.components_registry
    if registry.type_infos == None:
        registry.load_type_infos()

    type_infos = registry.type_infos


    def update_component(self, context, field_name, definition, type_name):
        component_name = definition["short_name"]
        type_info = definition["typeInfo"] if "typeInfo" in definition else None
        type_def = definition["type"] if "type" in definition else None

        
        print("update in component", component_name, type_name, type_info, field_name)#, type_def, type_info,self,self.name , "context",context.object.name, "attribute name", field_name)
        print("definition", definition)


        value = self[field_name]
        if type_name == 'bool':
            value = bool(value)
        if type_name == 'enum':
            print("self", self, "context", context, value)
            value = definition["oneOf"][int(value)]
        print("setting custom property", component_name, "field name", field_name, " value to", value)

        
        if type_info == "TupleStruct":
            context.object[component_name] = value
        if type_info == "Struct":
            context.object[component_name] = value
        if type_info == "Enum":
            context.object[component_name] = value

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

        

        if is_component and type_info != "Value" and type_info != "List" and "bevy_bevy_blender_editor_basic_example" in component_name:
            print("entry", component_name, type_def, type_info)# definition)

            __annotations__ = {}

            field_names = []
            single_item = True# single item is default, for tupple structs with single types, or structs with no params,
            tupple_or_struct = None

            item_to_display = None # FIXME: this is for enums only , move around
          
            if has_properties:
                tupple_or_struct = "struct"
                __annotations__ = __annotations__ | process_properties(registry, definition, properties, update_component)
           

            if has_prefixItems:
                tupple_or_struct = "tupple"
                __annotations__ = __annotations__ | process_prefixItems(registry, definition, prefixItems, update_component)

            if is_enum:
                __annotations__ = __annotations__ | process_enum(registry, definition, update_component)
                    
            for a in __annotations__:
                field_names.append(a)

            print("DONE: __annotations__", __annotations__)
            print("")
            property_group_name = short_name+"_ui"
            # print("creating property group", property_group_name)
            property_group_class = type(property_group_name, (PropertyGroup,), { '__annotations__': __annotations__, 'single_item': single_item, 'field_names': field_names, 'tupple_or_struct':tupple_or_struct })
            
            bpy.utils.register_class(property_group_class)
            setattr(bpy.types.Object, property_group_name, PointerProperty(type=property_group_class))
            
            registry.register_component_ui(short_name+"_ui", property_group_class)


