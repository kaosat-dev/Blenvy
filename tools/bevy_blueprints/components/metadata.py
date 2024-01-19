import bpy
import json
from bpy.props import (StringProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty)
from bpy_types import (PropertyGroup)
from bpy.types import (CollectionProperty)

from .ui import property_group_value_to_custom_property_value


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
    components_metadata = object.components_meta.components
    to_remove = []
    for index, component_meta in enumerate(components_metadata):
        short_name = component_meta.name
        if short_name not in object.keys():
            print("component:", short_name, "present in metadata, but not in object")
            to_remove.append(index)
    for index in to_remove:
        components_metadata.remove(index)


# returns a component definition ( an entry in registry's type_infos) with matching short name or None if nothing has been found
def find_component_definition_from_short_name(short_name):
    registry = bpy.context.window_manager.components_registry
    long_name = registry.short_names_to_long_names.get(short_name, None)
    if long_name != None:
        return registry.type_infos.get(long_name, None)
    return None

# FIXME: feels a bit heavy duty, should only be done
# if the components panel is active ?
def ensure_metadata_for_all_objects():
    for object in bpy.data.objects:
        add_metadata_to_components_without_metadata(object)

def add_metadata_to_components_without_metadata(object):
    components_metadata = object.components_meta.components # TODO: should we check for this

    for component_name in dict(object) :
        if component_name == "components_meta":
            continue
        component_meta =  next(filter(lambda component: component["name"] == component_name, components_metadata), None)
        if component_meta == None: 
            component_definition = find_component_definition_from_short_name(component_name)
            if component_definition == None:
                print("There is no component definition for component:", component_name)
            else:
                long_name = component_definition.long_name
                short_name = component_definition.name

                component_meta = components_metadata.add()
                component_meta.name = short_name
                component_meta.long_name = long_name
                print("added metadata for component: ", component_name)



# adds a component to an object (including metadata) using the provided component definition & optional value
def add_component_to_object(object, component_definition, value=None):
    cleanup_invalid_metadata(object)
    if object is not None:
        print("add_component_to_object", component_definition)
        long_name = component_definition["title"]
        short_name = component_definition["short_name"]

        components_metadata = object.components_meta.components
        matching_component = next(filter(lambda component: component["name"] == short_name, components_metadata), None)
        print("matching", matching_component)
        # matching component means we already have this type of component 
        if matching_component:
            return False
        
        component_meta = components_metadata.add()
        component_meta.name = short_name
        component_meta.long_name = long_name

        # now we use our pre_generated property groups to set the initial value of our custom property
        print("getting matching property group to set defaults")
        prop_group_name = short_name+"_ui"
        propertyGroup = getattr(object, prop_group_name)

        registry = bpy.context.window_manager.components_registry
        if registry.type_infos == None:
            # TODO: throw error
            print("registry type infos have not been loaded yet or ar missing !")
        definition = registry.type_infos[long_name]
        print("component definition", definition)
        value = property_group_value_to_custom_property_value(propertyGroup, definition)
        object[short_name] = value
