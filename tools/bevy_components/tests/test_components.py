import bpy



def test_add_components():
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

        print("add component", component_type)
        try:
            add_component_operator(component_type=component_type)

            property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
            object = bpy.context.object

            target_components_metadata = object.components_meta.components
            component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
            propertyGroup = getattr(component_meta, property_group_name, None)
            print("propertyGroup", propertyGroup, propertyGroup.field_names)
            added_components.append(component_type)
        except Exception as error:
            errors.append(error)
    print("added", len(added_components))
    assert len(errors) == 1
    """copy_component_operator = bpy.ops.object.copy_component
    copy_component_operator()"""

    #assert propertyGroup.field_names == ['a', 'b', 'c']

def test_remove_components():
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

        print("add component", component_type)
        try:
            add_component_operator(component_type=component_type)

            property_group_name = registry.get_propertyGroupName_from_shortName(short_name)
            object = bpy.context.object

            target_components_metadata = object.components_meta.components
            component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
            propertyGroup = getattr(component_meta, property_group_name, None)
            print("propertyGroup", propertyGroup, propertyGroup.field_names)
            added_components.append(component_type)
        except Exception as error:
            errors.append(error)
    print("added", len(added_components))
    assert len(errors) == 1

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

    """copy_component_operator = bpy.ops.object.copy_component
    copy_component_operator()"""
    

def test_copy_paste_components():
    context = bpy.context
    registry = context.window_manager.components_registry
    registry.schemaPath = "../../testing/bevy_registry_export/basic/assets/registry.json"
    bpy.ops.object.reload_registry()

    component_type = "bevy_bevy_registry_export_basic_example::test_components::BasicTest"
    short_name = "BasicTest"

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
