import bpy
from bpy.props import (StringProperty, BoolProperty, PointerProperty)
from bpy_types import (PropertyGroup)
from ..propGroups.conversions import property_group_value_from_custom_property_value, property_group_value_to_custom_property_value

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

    enabled: BoolProperty(
        name="enabled",
        description="component enabled",
        default=True
    )

    invalid: BoolProperty(
        name="invalid",
        description="component is invalid, because of missing registration/ other issues",
        default=False
    )

    invalid_details: StringProperty(
        name="invalid details",
        description="detailed information about why the component is invalid",
        default=""
    )

    visible: BoolProperty( # REALLY dislike doing this for UI control, but ok hack for now
        default=True
    )

class ComponentsMeta(PropertyGroup):
    infos_per_component:  StringProperty(
        name="infos per component",
        description="component"
    )
    components: bpy.props.CollectionProperty(type = ComponentInfos)  

    @classmethod
    def register(cls):
        bpy.types.Object.components_meta = PointerProperty(type=ComponentsMeta)

    @classmethod
    def unregister(cls):
        del bpy.types.Object.components_meta

# We need a collection property of components PER object
def get_component_metadata_by_short_name(object, short_name):
    if not "components_meta" in object:
        return None
    return next(filter(lambda component: component["name"] == short_name, object.components_meta.components), None)

# remove no longer valid metadata from object
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


def do_object_custom_properties_have_missing_metadata(object):
    components_metadata = getattr(object, "components_meta", None)
    if components_metadata == None:
        return True

    components_metadata = components_metadata.components
    registry = bpy.context.window_manager.components_registry

    missing_metadata = False
    for component_name in dict(object) :
        if component_name == "components_meta":
            continue
        component_meta =  next(filter(lambda component: component["name"] == component_name, components_metadata), None)
        if component_meta == None: 
            # current component has no metadata but is there even a compatible type in the registry ?
            # if not ignore it
            component_definition = find_component_definition_from_short_name(component_name)
            if component_definition != None:
                missing_metadata = True
                break
    return missing_metadata


# adds metadata to object only if it is missing
def add_metadata_to_components_without_metadata(object):
    components_metadata = object.components_meta.components # TODO: should we check for this
    registry = bpy.context.window_manager.components_registry

    for component_name in dict(object) :
        print("scanning", component_name)
        if component_name == "components_meta":
            continue
        component_meta =  next(filter(lambda component: component["name"] == component_name, components_metadata), None)
        if component_meta == None: 
            component_definition = find_component_definition_from_short_name(component_name)
            if component_definition == None:
                print("There is no component definition for component:", component_name)
            else:
                print("component_definition", component_definition)
                long_name = component_definition["title"]
                short_name = component_definition["short_name"]

                component_meta = components_metadata.add()
                component_meta.name = short_name
                component_meta.long_name = long_name

                property_group_name = short_name+"_ui"
                propertyGroup = getattr(component_meta, property_group_name, None)
                # this is unlikely to happen as the object would need to be missing both propgroup AND metadata
                if propertyGroup == None:
                    print("propertygroup not found injecting")
                    # we have not found a matching property_group, so try to inject it
                    setattr(ComponentInfos, property_group_name, registry.component_propertyGroups[property_group_name])
                    propertyGroup =  getattr(component_meta, property_group_name)

                property_group_value_from_custom_property_value(propertyGroup, component_definition, registry, object[component_name])
        else: # this one has metadata but we ensure that the relevant property group is already present
            short_name = component_meta.name 
            component_definition = find_component_definition_from_short_name(component_name)
            property_group_name = short_name+"_ui"
            propertyGroup = getattr(component_meta, property_group_name, None)
            if propertyGroup == None:
                print("propertygroup not found in metadata attempting to injectt")
                if property_group_name in registry.component_propertyGroups:
                    # we have found a matching property_group, so try to inject it
                    setattr(ComponentInfos, property_group_name, registry.component_propertyGroups[property_group_name])
                    propertyGroup =  getattr(component_meta, property_group_name)
            if propertyGroup != None:
                property_group_value_from_custom_property_value(propertyGroup, component_definition, registry, object[component_name])
            else:
                # if we still have not found the property group, mark it as invalid
                component_meta.enabled = False
                component_meta.invalid = True
                component_meta.invalid_details = "component type not present in the schema, possibly renamed ? Disabling for now"

# adds a component to an object (including metadata) using the provided component definition & optional value
def add_component_to_object(object, component_definition, value=None):
    cleanup_invalid_metadata(object)
    if object is not None:
        print("add_component_to_object", component_definition)
        long_name = component_definition["title"]
        short_name = component_definition["short_name"]

        components_metadata = object.components_meta.components
        matching_component = next(filter(lambda component: component["name"] == short_name, components_metadata), None)
        # matching component means we already have this type of component 
        if matching_component:
            return False
        
        component_meta = components_metadata.add()
        component_meta.name = short_name
        component_meta.long_name = long_name

        # now we use our pre_generated property groups to set the initial value of our custom property
        registry = bpy.context.window_manager.components_registry

        property_group_name = short_name+"_ui"
        propertyGroup = registry.component_propertyGroups[property_group_name]
        setattr(ComponentInfos, property_group_name, propertyGroup) # FIXME: not ideal as all ComponentInfos get the propGroup, but have not found a way to assign it per instance
        propertyGroup = getattr(component_meta, property_group_name)


        if registry.type_infos == None:
            # TODO: throw error
            print("registry type infos have not been loaded yet or ar missing !")

        definition = registry.type_infos[long_name]

        if value == None:
            value = property_group_value_to_custom_property_value(propertyGroup, definition, registry, None)
        else: # we have provided a value, that is a raw , custom property value, to set the value of the propertyGroup
            object["__disable__update"] = True # disable update callback while we set the values of the propertyGroup "tree" (as a propertyGroup can contain other propertyGroups) 
            property_group_value_from_custom_property_value(propertyGroup, definition, registry, value)
            del object["__disable__update"]

        #value_converted = value.to_dict() if "to_dict" in value else value
        object[short_name] = value
       
