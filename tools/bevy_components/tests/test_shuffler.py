import bpy
from .component_values_shuffler import component_values_shuffler

def test_shuffler():
    registry = bpy.context.window_manager.components_registry
    registry.schemaPath = "../../testing/bevy_registry_export/basic/assets/registry.json"
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos
    object = bpy.context.object

    add_component_operator = bpy.ops.object.add_bevy_component

    short_name = "BasicTest"
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
    

    # Testing a more complex component
    short_name = "NestingTestLevel2"
    component_type = registry.short_names_to_long_names[short_name]
    add_component_operator(component_type=component_type)


    property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)

    definition = type_infos[component_type]
    component_values_shuffler(seed= 17, property_group=propertyGroup, definition=definition, registry=registry)

    print("propertyGroup", object[short_name])
    # cheating / making things easier for us for complex types: we use the custom property value
    assert object[short_name] == '(basic: (a: 0.5219839215278625, b: 38, c: "ljfywwrv"), color: (Rgba(red:0.2782765030860901, green:0.9174930453300476, blue:0.24890311062335968, alpha:0.815186083316803)), colors_list: ([Rgba(red:0.2523837685585022, green:0.5016026496887207, blue:0.317435085773468, alpha:0.8463277816772461), Rgba(red:0.945193886756897, green:0.4015909433364868, blue:0.9984470009803772, alpha:0.06219279021024704)]), enable: true, enum_inner: Wood, nested: (vec: (Vec3(x:0.1509154736995697, y:0.7055686116218567, z:0.5588918924331665))), text: "vgkrdwuc", toggle: (false))'


    # And another complex component
    short_name = "EnumComplex"
    component_type = registry.short_names_to_long_names[short_name]
    add_component_operator(component_type=component_type)


    property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)

    definition = type_infos[component_type]
    component_values_shuffler(seed= 17, property_group=propertyGroup, definition=definition, registry=registry)

    print("propertyGroup", object[short_name])
    # cheating / making things easier for us for complex types: we use the custom property value
    assert object[short_name] == 'StructLike(a: 0.41416797041893005, b: 38, c: "ljfywwrv")'

    # And another complex component
    short_name = "AnimationPlayer"
    component_type = registry.short_names_to_long_names[short_name]
    add_component_operator(component_type=component_type)


    property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)

    definition = type_infos[component_type]
    component_values_shuffler(seed= 17, property_group=propertyGroup, definition=definition, registry=registry)

    print("propertyGroup", object[short_name])
    # cheating / making things easier for us for complex types: we use the custom property value
    assert object[short_name] == '(animation: "", paused: true)'



    # And another complex component
    short_name = "VecOfColors"
    component_type = registry.short_names_to_long_names[short_name]
    add_component_operator(component_type=component_type)


    property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)

    definition = type_infos[component_type]
    component_values_shuffler(seed= 17, property_group=propertyGroup, definition=definition, registry=registry)

    print("propertyGroup", object[short_name])
    # cheating / making things easier for us for complex types: we use the custom property value
    assert object[short_name] == '([Rgba(red:0.8066907525062561, green:0.9604947566986084, blue:0.2896253764629364, alpha:0.766107439994812), Rgba(red:0.7042198777198792, green:0.6613830327987671, blue:0.11016204953193665, alpha:0.02693677879869938)])'
    

    # And another complex component
    short_name = "VecOfF32s"
    component_type = registry.short_names_to_long_names[short_name]
    add_component_operator(component_type=component_type)

    property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)

    definition = type_infos[component_type]
    component_values_shuffler(seed= 17, property_group=propertyGroup, definition=definition, registry=registry)

    print("propertyGroup", object[short_name])
    # cheating / making things easier for us for complex types: we use the custom property value
    assert object[short_name] == '([0.8066907525062561, 0.9604947566986084])'

    # And another complex component
    short_name = "SkinnedMesh"
    component_type = registry.short_names_to_long_names[short_name]
    add_component_operator(component_type=component_type)

    property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
    target_components_metadata = object.components_meta.components
    component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
    propertyGroup = getattr(component_meta, property_group_name, None)

    definition = type_infos[component_type]
    component_values_shuffler(seed= 17, property_group=propertyGroup, definition=definition, registry=registry)

    print("propertyGroup", object[short_name])
    # cheating / making things easier for us for complex types: we use the custom property value
    assert object[short_name] == '(inverse_bindposes: Weak(Uuid(uuid: "73b3b118-7d01-4778-8bcc-4e79055f5d22")), joints: [0, 0])'
    