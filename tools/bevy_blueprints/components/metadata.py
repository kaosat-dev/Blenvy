import bpy
import json
from bpy.props import (StringProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty)
from bpy_types import (PropertyGroup)
from bpy.types import (CollectionProperty)


class ComponentInfos(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(
        name = "name",
        default = ""
    )

    long_name : bpy.props.StringProperty(
        name = "long name",
        default = ""
    )

    type_name : bpy.props.StringProperty(
        name = "Type",
        default = ""
    )

    values: bpy.props.StringProperty(
        name = "Value",
        default = ""
    )

    values: bpy.props.StringProperty(
        name = "Values",
        default = "[]"
    )

    data: bpy.props.StringProperty(
        name = "Toto",
        default = "[]"
    )
    enabled: BoolProperty(
        name="enabled",
        description="component enabled",
        default=True
    )


class ComponentsMeta(PropertyGroup):
    infos_per_component:  StringProperty(
        name="infos per component",
        description="component"
    )
    components: bpy.props.CollectionProperty(type = ComponentInfos)  

# We need a collection property of components PER object
def get_component_metadata_by_short_name(object, short_name):
    if not "components_meta" in object:
        return None
    return next(filter(lambda component: component["name"] == short_name, object.components_meta.components), None)

def cleanup_invalid_metadata(object):
    components_in_object = object.components_meta.components
    to_remove = []
    for index, component_meta in enumerate(components_in_object):
        short_name = component_meta.name
        if short_name not in object.keys():
            print("component:", short_name, "present in metadata, but not in object")
            to_remove.append(index)
    for index in to_remove:
        components_in_object.remove(index)


# returns a componentDefinition with matching short name or None if nothing has been found
def find_component_definition_from_short_name(short_name):
    component_definitions = bpy.context.window_manager.component_definitions
    for component_definition in component_definitions:
        if component_definition.name == short_name:
            return component_definition
    return None

# FIXME: feels a bit heavy duty, should only be done
# if the components panel is active ?
def ensure_metadata_for_all_objects():
    for object in bpy.data.objects:
        add_metadata_to_components_without_metadata(object)

def add_metadata_to_components_without_metadata(object):
    components_in_object = object.components_meta.components # TODO: should we check for this

    for component_name in dict(object) :
        if component_name == "components_meta":
            continue
        component_meta =  next(filter(lambda component: component["name"] == component_name, components_in_object), None)
        if component_meta == None: 
            component_definition = find_component_definition_from_short_name(component_name)
            if component_definition == None:
                print("There is no component definition for component:", component_name)
            else:
                long_name = component_definition.long_name
                short_name = component_definition.name
                data = json.loads(component_definition.data)

                component_meta = components_in_object.add()
                component_meta.name = short_name
                component_meta.long_name = long_name
                component_meta.data = component_definition.data
                component_meta.type_name = data["type"]
                print("added metadata for component: ", component_name)



# adds a component to an object (including metadata) using the provided componentDefinition & optional value
def add_component_to_object(object, component_definition, value=None):
    cleanup_invalid_metadata(object)
    if object is not None:
        long_name = component_definition.long_name
        short_name = component_definition.name
        data = json.loads(component_definition.data)

      
        print("component infos", data, "long_name", component_definition.long_name)
        type_name = data["type"]
        default_value = data["value"]

        def make_bool():
            object[component_definition.name] = default_value

        def make_string():
            object[component_definition.name] = default_value

        def make_color():
            object[component_definition.name] = default_value
            property_manager = object.id_properties_ui(component_definition.name)
            property_manager.update(subtype='COLOR')

        def make_enum():
            object[component_definition.name] = component_definition.values

        component_prop_makers = {
            "Bool": make_bool,
            "Color": make_color,
            "String":make_string,
            "Enum":make_enum
        }

        if type_name in component_prop_makers:
            component_prop_makers[type_name]()
        else :
            object[component_definition.name] = default_value

        if value is not None:
            object[component_definition.name] = value


        """
        registry = bpy.context.window_manager.components_registry.registry 
        registry = json.loads(registry)
        registry_entry = registry[long_name] if long_name in registry else None
        print("registry_entry", registry_entry)
        """

        #object.components_meta.components.clear()
        components_in_object = object.components_meta.components

        matching_component = next(filter(lambda component: component["name"] == short_name, components_in_object), None)
        print("matching", matching_component)
        # matching component means we already have this type of component 
        if matching_component:
            return False
        
        component_meta = components_in_object.add()
        component_meta.name = short_name
        component_meta.long_name = long_name
        component_meta.data = component_definition.data
        component_meta.type_name = data["type"]

        prop_group_name = short_name+"_ui"
        propertyGroup = getattr(object, prop_group_name)

        print("propertyGroup", propertyGroup, propertyGroup.field_names)

        propertyGroup['0'] = value

        """
        object[component_definition.name] = 0.5
        property_manager = object.id_properties_ui(component_definition.name)
        property_manager.update(min=-10, max=10, soft_min=-5, soft_max=5)

        print("property_manager", property_manager)

        object[component_definition.name] = [0.8,0.2,1.0]
        property_manager = object.id_properties_ui(component_definition.name)
        property_manager.update(subtype='COLOR')"""

        #IDPropertyUIManager
        #rna_ui = object[component_definition.name].get('_RNA_UI')


