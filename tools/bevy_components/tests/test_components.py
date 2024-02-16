import bpy
import pytest
import pprint

from ..propGroups.conversions_to_prop_group import property_group_value_from_custom_property_value
from ..propGroups.conversions_from_prop_group import property_group_value_to_custom_property_value
from .component_values_shuffler import component_values_shuffler
from .expected_component_values import (expected_custom_property_values, expected_custom_property_values_randomized)

@pytest.fixture
def setup_data(request):
    print("\nSetting up resources...")

    def finalizer():
        print("\nPerforming teardown...")
        registry = bpy.context.window_manager.components_registry
        #registry.schemaPath = "../../testing/bevy_registry_export/basic/assets/registry.json"
        #bpy.ops.object.reload_registry()

        type_infos = registry.type_infos
        object = bpy.context.object
        remove_component_operator = bpy.ops.object.delete_component

        for type_name in type_infos:
            definition = type_infos[type_name]
            component_name = definition["short_name"]
            if component_name in object:
                try:
                    remove_component_operator(component_name=component_name)
                except Exception as error:
                    pass

    request.addfinalizer(finalizer)

    return None


def test_components_should_generate_correct_custom_properties(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schemaPath = "../../testing/bevy_registry_export/basic/assets/registry.json"
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos
    object = bpy.context.object

    add_component_operator = bpy.ops.object.add_component
    errors = []
    addable_components = []
    added_components = []

    custom_property_values = {}
    
    for type_name in type_infos:
        definition = type_infos[type_name]
        component_type = definition["title"]
        short_name = definition["short_name"]
        is_component = definition['isComponent']  if "isComponent" in definition else False
        if not is_component:
            continue

        addable_components.append(component_type)

        try:
            add_component_operator(component_type=component_type)

            property_group_name = registry.get_propertyGroupName_from_shortName(short_name)

            target_components_metadata = object.components_meta.components
            component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
            propertyGroup = getattr(component_meta, property_group_name, None)
            added_components.append(component_type)
            custom_property_values[short_name] = object[short_name]
            assert object[short_name] == expected_custom_property_values[short_name]

        except Exception as error:
            errors.append(error)

    """pp = pprint.PrettyPrinter(depth=14, width=120)
    print("CUSTOM PROPERTY VALUES")
    pp.pprint(custom_property_values)"""

    assert len(errors) == 0
    assert len(added_components) == 151

    
def test_components_should_generate_correct_custom_properties_with_randomozied_values(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schemaPath = "../../testing/bevy_registry_export/basic/assets/registry.json"
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos
    object = bpy.context.object

    add_component_operator = bpy.ops.object.add_component
    errors = []
    error_components = []
    addable_components = []
    added_components = []

    custom_property_values = {}
    
    for type_name in type_infos:
        definition = type_infos[type_name]
        component_type = definition["title"]
        short_name = definition["short_name"]
        is_component = definition['isComponent']  if "isComponent" in definition else False
        if not is_component:
            continue

        addable_components.append(component_type)

        try:
            add_component_operator(component_type=component_type)
            property_group_name = registry.get_propertyGroupName_from_shortName(short_name)

            target_components_metadata = object.components_meta.components
            component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
            propertyGroup = getattr(component_meta, property_group_name, None)
            component_values_shuffler(seed= 10, property_group=propertyGroup, definition=definition, registry=registry)

            added_components.append(component_type)
            custom_property_values[short_name] = object[short_name]
            assert object[short_name] == expected_custom_property_values_randomized[short_name]

        except Exception as error:
            errors.append(error)
            error_components.append(short_name)

    """pp = pprint.PrettyPrinter(depth=14, width=120)
    print("CUSTOM PROPERTY VALUES")
    pp.pprint(custom_property_values)"""

    print("error_components", error_components)
    assert len(errors) == 0
    assert len(added_components) == 151

def test_components_should_generate_correct_propertyGroup_values_from_custom_properties(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schemaPath = "../../testing/bevy_registry_export/basic/assets/registry.json"
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos
    object = bpy.context.object

    add_component_operator = bpy.ops.object.add_component
    errors = []
    addable_components = []
    added_components = []
    failing_components = []

    for type_name in type_infos:
        definition = type_infos[type_name]
        component_type = definition["title"]
        short_name = definition["short_name"]
        is_component = definition['isComponent']  if "isComponent" in definition else False
        if not is_component:
            continue

        addable_components.append(component_type)

        try:
            add_component_operator(component_type=component_type)
            property_group_name = registry.get_propertyGroupName_from_shortName(short_name)

            target_components_metadata = object.components_meta.components
            component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
            propertyGroup = getattr(component_meta, property_group_name, None)
            added_components.append(component_type)
            # randomise values
            component_values_shuffler(seed= 10, property_group=propertyGroup, definition=definition, registry=registry)
            custom_property_value = object[short_name]

            # first check if custom property value matches what we expect
            assert custom_property_value == expected_custom_property_values_randomized[short_name]

            # we update propgroup values from custom property values
            property_group_value_from_custom_property_value(propertyGroup, definition, registry, custom_property_value, nesting = [])
            # and then generate it back
            custom_property_value_regen = property_group_value_to_custom_property_value(propertyGroup, definition, registry, None)
            assert custom_property_value_regen == expected_custom_property_values_randomized[short_name]

            # custom_property_values[short_name] = object[short_name]
            #assert object[short_name] == expected_custom_property_values[short_name]
            #print("CUSTOM PROPERTY ", object[short_name])

        except Exception as error:
            errors.append(error)
            failing_components.append(short_name)

    for index, error in enumerate(errors):
        print("ERROR", error, failing_components[index])
    assert len(errors) == 0
    assert len(added_components) == 151


def test_remove_components(setup_data):
    registry = bpy.context.window_manager.components_registry
    registry.schemaPath = "../../testing/bevy_registry_export/basic/assets/registry.json"
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos

    add_component_operator = bpy.ops.object.add_component
    errors = []
    addable_components = []
    added_components = []

    for type_name in type_infos:
        definition = type_infos[type_name]
        component_type = definition["title"]
        short_name = definition["short_name"]
        is_component = definition['isComponent']  if "isComponent" in definition else False
        if not is_component:
            continue

        addable_components.append(component_type)

        try:
            add_component_operator(component_type=component_type)

            property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
            object = bpy.context.object

            target_components_metadata = object.components_meta.components
            component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
            propertyGroup = getattr(component_meta, property_group_name, None)
            # print("propertyGroup", propertyGroup, propertyGroup.field_names)
            added_components.append(component_type)
        except Exception as error:
            errors.append(error)
    assert len(errors) == 0

    # now test component removal
    errors.clear()
    remove_component_operator = bpy.ops.object.delete_component
    for component_type in added_components:
        component_name = type_infos[component_type]["short_name"]
        try:
            remove_component_operator(component_name=component_name)
        except Exception as error:
            errors.append(error)
    assert len(errors) == 0
    
def test_copy_paste_components(setup_data):
    context = bpy.context
    registry = context.window_manager.components_registry
    registry.schemaPath = "../../testing/bevy_registry_export/basic/assets/registry.json"
    bpy.ops.object.reload_registry()

    #component_type = "bevy_bevy_registry_export_basic_example::test_components::BasicTest"
    short_name = "BasicTest"
    component_type = registry.short_names_to_long_names[short_name]

    # SOURCE object setup
    add_component_operator = bpy.ops.object.add_component
    add_component_operator(component_type=component_type)

    property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
    object = context.object

    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)

    setattr(propertyGroup, propertyGroup.field_names[0], 25.0)

    copy_component_operator = bpy.ops.object.copy_component
    copy_component_operator(source_component_name=short_name, source_object_name=object.name)

    # ---------------------------------------
    # TARGET object 
    bpy.ops.mesh.primitive_cube_add()
    new_cube = bpy.context.selected_objects[0]
    # change name
    new_cube.name = "TargetCube"
    target_components_metadata = new_cube.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)

    # first check that there is no component currently
    assert component_meta == None

    paste_component_operator = bpy.ops.object.paste_component
    paste_component_operator()

    target_components_metadata = new_cube.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)

    # now after pasting to the new object, it should have component meta
    assert component_meta != None

    # and then check if the propertyGroup of the target object is correct
    propertyGroup = getattr(component_meta, property_group_name, None)
    assert propertyGroup.field_names == ['a', 'b', 'c']

    a_fieldValue = getattr(propertyGroup, propertyGroup.field_names[0])
    assert a_fieldValue == 25.0

