import bpy

from ..propGroups.conversions_to_prop_group import property_group_value_from_custom_property_value
from ..propGroups.conversions_from_prop_group import property_group_value_to_custom_property_value


def test_add_components():
    registry = bpy.context.window_manager.components_registry
    registry.schemaPath = "../../testing/bevy_registry_export/basic/assets/registry.json"
    bpy.ops.object.reload_registry()

    type_infos = registry.type_infos
    object = bpy.context.object

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

            target_components_metadata = object.components_meta.components
            component_meta = next(filter(lambda component: component["name"] == short_name, target_components_metadata), None)
            propertyGroup = getattr(component_meta, property_group_name, None)
            added_components.append(component_type)
        except Exception as error:
            errors.append(error)

    assert len(errors) == 1
    assert len(added_components) == 150
    #assert propertyGroup.field_names == ['a', 'b', 'c']

import pprint


expected_custom_property_values = {
        'Aabb': '(center: Vec3A(x:0.0, y:0.0, z:0.0), half_extents: Vec3A(x:0.0, y:0.0, z:0.0))',
        'AdditionalMassProperties': 'Mass(0.0)',
        'AmbientLightSettings': '(brightness: 0.0, color: Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0))',
        'AnimationPlayer': '(animation: "", paused: true)',
        'Animations': '(named_animations: "")',
        'AutoAABBCollider': 'Cuboid',
        'BackgroundColor': '(Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0))',
        'BasicTest': '(a: 0.0, b: 0, c: " ")',
        'BloomSettings': '(composite_mode: EnergyConserving, high_pass_frequency: 0.0, intensity: 0.0, low_frequency_boost: '
                        '0.0, low_frequency_boost_curvature: 0.0, prefilter_settings: (threshold: 0.0, threshold_softness: '
                        '0.0))',
        'BlueprintName': '(" ")',
        'BorderColor': '(Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0))',
        'Button': '',
        'CalculatedClip': '(clip: (max: Vec2(x:0.0, y:0.0), min: Vec2(x:0.0, y:0.0)))',
        'Camera': '(hdr: true, is_active: true, msaa_writeback: true, order: '
                'bpy.data.objects[Cube].components_meta.components[103].589_ui.order, viewport: None)',
        'Camera2d': '(clear_color: Default)',
        'Camera3d': '(clear_color: Default, depth_load_op: Clear(0.0), depth_texture_usages: "", '
                    'screen_space_specular_transmission_quality: "", screen_space_specular_transmission_steps: '
                    'bpy.data.objects[Cube].components_meta.components[47].345_ui.screen_space_specular_transmission_steps)',
        'CameraRenderGraph': '(bpy.data.objects[Cube].components_meta.components[104].591_ui.0)',
        'CameraTrackable': '',
        'CameraTracking': '(offset: Vec3(x:0.0, y:0.0, z:0.0))',
        'CameraTrackingOffset': '(Vec3(x:0.0, y:0.0, z:0.0))',
        'CascadeShadowConfig': '(bounds: "", minimum_distance: 0.0, overlap_proportion: 0.0)',
        'Cascades': '(cascades: "")',
        'CascadesFrusta': '',
        'CascadesVisibleEntities': '',
        'Ccd': '(enabled: true)',
        'Children': '([])',
        'ClusterConfig': 'None',
        'Collider': 'Ball(0.0)',
        'CollidingEntities': '("")',
        'CollisionGroups': '(filters: (0), memberships: (0))',
        'ColorGrading': '(exposure: 0.0, gamma: 0.0, post_saturation: 0.0, pre_saturation: 0.0)',
        'ContactForceEventThreshold': '(0.0)',
        'ContentSize': '',
        'ContrastAdaptiveSharpeningSettings': '(denoise: true, enabled: true, sharpening_strength: 0.0)',
        'CubemapFrusta': '',
        'CubemapVisibleEntities': '',
        'Damping': '(angular_damping: 0.0, linear_damping: 0.0)',
        'DebandDither': 'Disabled',
        'DirectionalLight': '(color: Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0), illuminance: 0.0, shadow_depth_bias: 0.0, '
                            'shadow_normal_bias: 0.0, shadows_enabled: true)',
        'Dominance': '(groups: 0)',
        'EnumComplex': 'Float(0.0)',
        'EnumTest': 'Metal',
        'ExternalForce': '(force: Vec3(x:0.0, y:0.0, z:0.0), torque: Vec3(x:0.0, y:0.0, z:0.0))',
        'ExternalImpulse': '(impulse: Vec3(x:0.0, y:0.0, z:0.0), torque_impulse: Vec3(x:0.0, y:0.0, z:0.0))',
        'FocusPolicy': 'Block',
        'FogSettings': '(color: Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0), directional_light_color: Rgba(red:1.0, '
                        'green:1.0, blue:0.0, alpha:1.0), directional_light_exponent: 0.0, falloff: "")',
        'Friction': '(coefficient: 0.0, combine_rule: "")',
        'Frustum': '',
        'Fxaa': '(edge_threshold: "", edge_threshold_min: "", enabled: true)',
        'GlobalTransform': '((matrix3: (x_axis: Vec3A(x:0.0, y:0.0, z:0.0), y_axis: Vec3A(x:0.0, y:0.0, z:0.0), z_axis: '
                            'Vec3A(x:0.0, y:0.0, z:0.0)), translation: Vec3A(x:0.0, y:0.0, z:0.0)))',
        'GltfExtras': '(value: " ")',
        'GravityScale': '(0.0)',
        'Group': '(0)',
        'Handle<()>': 'Strong("")',
        'Handle<AnimationClip>': 'Strong("")',
        'Handle<AudioSource>': 'Strong("")',
        'Handle<ColorMaterial>': 'Strong("")',
        'Handle<DynamicScene>': 'Strong("")',
        'Handle<Font>': 'Strong("")',
        'Handle<Gltf>': 'Strong("")',
        'Handle<GltfMesh>': 'Strong("")',
        'Handle<GltfNode>': 'Strong("")',
        'Handle<GltfPrimitive>': 'Strong("")',
        'Handle<Image>': 'Strong("")',
        'Handle<LineGizmo>': 'Strong("")',
        'Handle<LoadedFolder>': 'Strong("")',
        'Handle<LoadedUntypedAsset>': 'Strong("")',
        'Handle<Mesh>': 'Strong("")',
        'Handle<Pitch>': 'Strong("")',
        'Handle<Scene>': 'Strong("")',
        'Handle<Shader>': 'Strong("")',
        'Handle<SkinnedMeshInverseBindposes>': 'Strong("")',
        'Handle<StandardDynamicAssetCollection>': 'Strong("")',
        'Handle<StandardMaterial>': 'Strong("")',
        'Handle<TextureAtlas>': 'Strong("")',
        'Handle<WireframeMaterial>': 'Strong("")',
        'InheritedVisibility': '(true)',
        'Interaction': 'Pressed',
        'Label': '',
        'LockedAxes': '(0)',
        'MaterialInfo': '(name: " ", source: " ")',
        'Mesh2dHandle': '(Strong(\\""\\))',
        'MeshMorphWeights': '(weights: "")',
        'MorphWeights': '(first_mesh: "", weights: "")',
        'Name': '(hash: 0, name: bpy.data.objects[Cube].components_meta.components[43].327_ui.name)',
        'NestedTupleStuff': '(0.0, 0, (basic: (a: 0.0, b: 0, c: " "), color: (Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0)), '
                            'colors_list: ([]), enable: true, enum_inner: Metal, nested: (vec: (Vec3(x:0.0, y:0.0, z:0.0))), '
                            'text: " ", toggle: (true)))',
        'NestingTestLevel2': '(basic: (a: 0.0, b: 0, c: " "), color: (Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0)), '
                            'colors_list: ([]), enable: true, enum_inner: Metal, nested: (vec: (Vec3(x:0.0, y:0.0, z:0.0))), '
                            'text: " ", toggle: (true))',
        'NestingTestLevel3': '(vec: (Vec3(x:0.0, y:0.0, z:0.0)))',
        'NoFrustumCulling': '',
        'NoWireframe': '',
        'Node': '(calculated_size: Vec2(x:0.0, y:0.0), outline_offset: 0.0, outline_width: 0.0, stack_index: 0, '
                'unrounded_size: Vec2(x:0.0, y:0.0))',
        'NotShadowCaster': '',
        'NotShadowReceiver': '',
        'OrthographicProjection': '(area: (max: Vec2(x:0.0, y:0.0), min: Vec2(x:0.0, y:0.0)), far: 0.0, near: 0.0, scale: '
                                '0.0, scaling_mode: "Fixed(height: 0.0, width: 0.0)", viewport_origin: Vec2(x:0.0, y:0.0))',
        'Outline': '(color: Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0), offset: Auto, width: Auto)',
        'Parent': '(bpy.data.objects[Cube].components_meta.components[68].381_ui.0)',
        'PerspectiveProjection': '(aspect_ratio: 0.0, far: 0.0, fov: 0.0, near: 0.0)',
        'Pickable': '',
        'Player': '',
        'PointLight': '(color: Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0), intensity: 0.0, radius: 0.0, range: 0.0, '
                    'shadow_depth_bias: 0.0, shadow_normal_bias: 0.0, shadows_enabled: true)',
        'PrimaryWindow': '',
        'Projection': 'Perspective((aspect_ratio: 0.0, far: 0.0, fov: 0.0, near: 0.0))',
        'RelativeCursorPosition': '(normalized: "", normalized_visible_node_rect: (max: Vec2(x:0.0, y:0.0), min: Vec2(x:0.0, '
                                'y:0.0)))',
        'RenderLayers': '(0)',
        'Restitution': '(coefficient: 0.0, combine_rule: "")',
        'RigidBody': 'Dynamic',
        'SSAOSettings': '',
        'ScreenSpaceAmbientOcclusionSettings': '(quality_level: "")',
        'Sensor': '',
        'ShadowFilteringMethod': 'Hardware2x2',
        'ShadowmapSettings': '(size: bpy.data.objects[Cube].components_meta.components[62].369_ui.size)',
        'SkinnedMesh': '(inverse_bindposes: Strong(\\""\\), joints: [])',
        'Sleeping': '(angular_threshold: 0.0, linear_threshold: 0.0, sleeping: true)',
        'SolverGroups': '(filters: (0), memberships: (0))',
        'SoundMaterial': 'Metal',
        'SpawnHere': '',
        'SpotLight': '(color: Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0), inner_angle: 0.0, intensity: 0.0, outer_angle: '
                    '0.0, radius: 0.0, range: 0.0, shadow_depth_bias: 0.0, shadow_normal_bias: 0.0, shadows_enabled: true)',
        'Sprite': '(anchor: Center, color: Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0), custom_size: "", flip_x: true, '
                'flip_y: true, rect: "")',
        'Style': '(align_content: Default, align_items: Default, align_self: Auto, aspect_ratio: None, border: (bottom: Auto, '
                'left: Auto, right: Auto, top: Auto), bottom: Auto, column_gap: Auto, direction: Inherit, display: Flex, '
                'flex_basis: Auto, flex_direction: Row, flex_grow: 0.0, flex_shrink: 0.0, flex_wrap: NoWrap, '
                'grid_auto_columns: "", grid_auto_flow: Row, grid_auto_rows: "", grid_column: (end: "", span: "", start: '
                '""), grid_row: (end: "", span: "", start: ""), grid_template_columns: "", grid_template_rows: "", height: '
                'Auto, justify_content: Default, justify_items: Default, justify_self: Auto, left: Auto, margin: (bottom: '
                'Auto, left: Auto, right: Auto, top: Auto), max_height: Auto, max_width: Auto, min_height: Auto, min_width: '
                'Auto, overflow: (x: Visible, y: Visible), padding: (bottom: Auto, left: Auto, right: Auto, top: Auto), '
                'position_type: Relative, right: Auto, row_gap: Auto, top: Auto, width: Auto)',
        'Text': '(alignment: Left, linebreak_behavior: WordBoundary, sections: [])',
        'Text2dBounds': '(size: Vec2(x:0.0, y:0.0))',
        'TextFlags': '(needs_new_measure_func: true, needs_recompute: true)',
        'TextLayoutInfo': '(glyphs: "", logical_size: Vec2(x:0.0, y:0.0))',
        'TextureAtlasSprite': '(anchor: Center, color: Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0), custom_size: "", '
                            'flip_x: true, flip_y: true, index: '
                            'bpy.data.objects[Cube].components_meta.components[124].721_ui.index)',
        'Tonemapping': 'None',
        'Transform': '(rotation: Quat(x:0.0, y:0.0, z:0.0, w:0.0), scale: Vec3(x:0.0, y:0.0, z:0.0), translation: Vec3(x:0.0, '
                    'y:0.0, z:0.0))',
        'TupleTest2': '(0.0, 0, " ")',
        'TupleTestBool': '(true)',
        'TupleTestColor': '(Rgba(red:1.0, green:1.0, blue:0.0, alpha:1.0))',
        'TupleTestF32': '(0.0)',
        'TupleTestStr': '(" ")',
        'TupleTestU64': '(0)',
        'TupleVec': '([])',
        'TupleVec2': '(Vec2(x:0.0, y:0.0))',
        'TupleVec3': '(Vec3(x:0.0, y:0.0, z:0.0))',
        'TupleVecF32F32': '([])',
        'UiCameraConfig': '(show_ui: true)',
        'UiImage': '(flip_x: true, flip_y: true, texture: Strong(\\""\\))',
        'UiImageSize': '(size: Vec2(x:0.0, y:0.0))',
        'UiTextureAtlasImage': '(flip_x: true, flip_y: true, index: '
                                'bpy.data.objects[Cube].components_meta.components[142].1075_ui.index)',
        'UnitTest': '',
        'VecOfColors': '([])',
        'VecOfVec3s2': '([])',
        'Velocity': '(angvel: Vec3(x:0.0, y:0.0, z:0.0), linvel: Vec3(x:0.0, y:0.0, z:0.0))',
        'ViewVisibility': '(true)',
        'Visibility': 'Inherited',
        'VisibleEntities': '',
        'Window': '(canvas: None, composite_alpha_mode: Auto, cursor: (grab_mode: None, hit_test: true, icon: Default, '
                'visible: true), decorations: true, enabled_buttons: (close: true, maximize: true, minimize: true), '
                'fit_canvas_to_parent: true, focused: true, ime_enabled: true, ime_position: Vec2(x:0.0, y:0.0), internal: '
                '(maximize_request: None, minimize_request: None, physical_cursor_position: None), mode: Windowed, '
                'position: Automatic, present_mode: AutoVsync, prevent_default_event_handling: true, resizable: true, '
                'resize_constraints: (max_height: 0.0, max_width: 0.0, min_height: 0.0, min_width: 0.0), resolution: '
                '(physical_height: 0, physical_width: 0, scale_factor: 0.0, scale_factor_override: None), title: " ", '
                'transparent: true, visible: true, window_level: AlwaysOnBottom, window_theme: "")',
        'Wireframe': '',
        'ZIndex': 'Local(0)'
        }


def test_components_should_generate_correct_custom_properties():
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
            #print("CUSTOM PROPERTY ", object[short_name])

        except Exception as error:
            errors.append(error)

    assert len(errors) == 1
    assert len(added_components) == 150

    """pp = pprint.PrettyPrinter(depth=14, width=120)
    print("CUSTOM PROPERTY VALUES")
    pp.pprint(custom_property_values)"""

def test_components_should_generate_correct_propertyGroup_values_from_custom_properties():
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

    #generate_propGroup_values_from_customProp_values_operator = bpy.ops.object.refresh_ui_from_custom_properties_current
    #generate_propGroup_values_from_customProp_values_operator()

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

            custom_property_value = object[short_name]
            # we update propgroup values from custom property values
            property_group_value_from_custom_property_value(propertyGroup, definition, registry, custom_property_value, nesting = [])
            # and then generate it back
            custom_property_value_regen = property_group_value_to_custom_property_value(propertyGroup, definition, registry, None)
            assert custom_property_value_regen == expected_custom_property_values[short_name]

            # custom_property_values[short_name] = object[short_name]
            #assert object[short_name] == expected_custom_property_values[short_name]
            #print("CUSTOM PROPERTY ", object[short_name])

        except Exception as error:
            errors.append(error)

    assert len(errors) == 1
    assert len(added_components) == 150


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

