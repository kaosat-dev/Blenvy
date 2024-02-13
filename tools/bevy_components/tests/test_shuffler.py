import bpy
from .component_values_shuffler import component_values_shuffler

def test_shuffler():
    registry = bpy.context.window_manager.components_registry
    registry.schemaPath = "../../testing/bevy_registry_export/basic/assets/registry.json"
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos
    object = bpy.context.object

    add_component_operator = bpy.ops.object.add_component


    """short_name = "BasicTest"
    component_type = registry.short_names_to_long_names[short_name]

    add_component_operator(component_type=component_type)

    property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)

    definition = type_infos[component_type]
    component_values_shuffler(seed= 10, property_group=propertyGroup, definition=definition, registry=registry)

    assert getattr(propertyGroup, 'a') == 0.5714026093482971
    assert getattr(propertyGroup, 'b') == 54
    assert getattr(propertyGroup, 'c') == "psagopiu"
    """

    # Testing a more complex component
    short_name = "NestingTestLevel2"
    component_type = registry.short_names_to_long_names[short_name]
    add_component_operator(component_type=component_type)


    property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)

    definition = type_infos[component_type]
    component_values_shuffler(seed= 10, property_group=propertyGroup, definition=definition, registry=registry)

    assert getattr(propertyGroup, 'a') == 0.5714026093482971
   


