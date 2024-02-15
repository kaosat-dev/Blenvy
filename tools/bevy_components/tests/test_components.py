import bpy

from ..propGroups.conversions_to_prop_group import property_group_value_from_custom_property_value
from ..propGroups.conversions_from_prop_group import property_group_value_to_custom_property_value
from .component_values_shuffler import component_values_shuffler

def _test_add_components():
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

    assert len(errors) == 0
    assert len(added_components) == 150
    #assert propertyGroup.field_names == ['a', 'b', 'c']

import pprint


expected_custom_property_values = {
 'AComponentWithAnExtremlyExageratedOrMaybeNotButCouldBeNameOrWut': '',
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
             'bpy.data.objects[Cube].components_meta.components[48].346_ui.screen_space_specular_transmission_steps)',
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
 'Name': '(hash: 0, name: bpy.data.objects[Cube].components_meta.components[44].328_ui.name)',
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
 'ZIndex': 'Local(0)'}


def _test_components_should_generate_correct_custom_properties():
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

    assert len(errors) == 0
    assert len(added_components) == 150

    """pp = pprint.PrettyPrinter(depth=14, width=120)
    print("CUSTOM PROPERTY VALUES")
    pp.pprint(custom_property_values)
    """

expected_custom_property_values_randomized = {
 'AComponentWithAnExtremlyExageratedOrMaybeNotButCouldBeNameOrWut': '',
 'Aabb': '(center: Vec3A(x:0.5714026093482971, y:0.42888906598091125, z:0.5780913233757019), half_extents: '
         'Vec3A(x:0.20609822869300842, y:0.8133212327957153, z:0.8235888481140137))',
 'AdditionalMassProperties': 'Mass(0.42888906598091125)',
 'AmbientLightSettings': '(brightness: 0.5714026093482971, color: Rgba(red:0.42888906598091125, '
                         'green:0.5780913233757019, blue:0.20609822869300842, alpha:0.8133212327957153))',
 'AnimationPlayer': '(animation: "", paused: true)',
 'Animations': '(named_animations: "")',
 'AutoAABBCollider': 'Capsule',
 'BackgroundColor': '(Rgba(red:0.5714026093482971, green:0.42888906598091125, blue:0.5780913233757019, '
                    'alpha:0.20609822869300842))',
 'BasicTest': '(a: 0.5714026093482971, b: 54, c: "psagopiu")',
 'BloomSettings': '(composite_mode: EnergyConserving, high_pass_frequency: 0.42888906598091125, intensity: '
                  '0.5780913233757019, low_frequency_boost: 0.20609822869300842, low_frequency_boost_curvature: '
                  '0.8133212327957153, prefilter_settings: (threshold: 0.8235888481140137, threshold_softness: '
                  '0.6534725427627563))',
 'BlueprintName': '("sbnpsago")',
 'BorderColor': '(Rgba(red:0.5714026093482971, green:0.42888906598091125, blue:0.5780913233757019, '
                'alpha:0.20609822869300842))',
 'Button': '',
 'CalculatedClip': '(clip: (max: Vec2(x:0.5714026093482971, y:0.42888906598091125), min: Vec2(x:0.5780913233757019, '
                   'y:0.20609822869300842)))',
 'Camera': '(hdr: true, is_active: false, msaa_writeback: false, order: 61, viewport: None)',
 'Camera2d': '(clear_color: None)',
 'Camera3d': '(clear_color: None, depth_load_op: Clear(0.42888906598091125), depth_texture_usages: "", '
             'screen_space_specular_transmission_quality: "", screen_space_specular_transmission_steps: 73)',
 'CameraRenderGraph': '("")',
 'CameraTrackable': '',
 'CameraTracking': '(offset: Vec3(x:0.5714026093482971, y:0.42888906598091125, z:0.5780913233757019))',
 'CameraTrackingOffset': '(Vec3(x:0.5714026093482971, y:0.42888906598091125, z:0.5780913233757019))',
 'CascadeShadowConfig': '(bounds: "", minimum_distance: 0.5714026093482971, overlap_proportion: 0.42888906598091125)',
 'Cascades': '(cascades: "")',
 'CascadesFrusta': '',
 'CascadesVisibleEntities': '',
 'Ccd': '(enabled: true)',
 'Children': '([])',
 'ClusterConfig': 'None',
 'Collider': 'Ball(0.42888906598091125)',
 'CollidingEntities': '("")',
 'CollisionGroups': '(filters: (73), memberships: (4))',
 'ColorGrading': '(exposure: 0.5714026093482971, gamma: 0.42888906598091125, post_saturation: 0.5780913233757019, '
                 'pre_saturation: 0.20609822869300842)',
 'ContactForceEventThreshold': '(0.5714026093482971)',
 'ContentSize': '',
 'ContrastAdaptiveSharpeningSettings': '(denoise: true, enabled: false, sharpening_strength: 0.42888906598091125)',
 'CubemapFrusta': '',
 'CubemapVisibleEntities': '',
 'Damping': '(angular_damping: 0.5714026093482971, linear_damping: 0.42888906598091125)',
 'DebandDither': 'Disabled',
 'DirectionalLight': '(color: Rgba(red:0.5714026093482971, green:0.42888906598091125, blue:0.5780913233757019, '
                     'alpha:0.20609822869300842), illuminance: 0.8133212327957153, shadow_depth_bias: '
                     '0.8235888481140137, shadow_normal_bias: 0.6534725427627563, shadows_enabled: false)',
 'Dominance': '(groups: 73)',
 'EnumComplex': 'StructLike(a: 0.03258506581187248, b: 61, c: "sagopiuz")',
 'EnumTest': 'Squishy',
 'ExternalForce': '(force: Vec3(x:0.5714026093482971, y:0.42888906598091125, z:0.5780913233757019), torque: '
                  'Vec3(x:0.20609822869300842, y:0.8133212327957153, z:0.8235888481140137))',
 'ExternalImpulse': '(impulse: Vec3(x:0.5714026093482971, y:0.42888906598091125, z:0.5780913233757019), '
                    'torque_impulse: Vec3(x:0.20609822869300842, y:0.8133212327957153, z:0.8235888481140137))',
 'FocusPolicy': 'Block',
 'FogSettings': '(color: Rgba(red:0.5714026093482971, green:0.42888906598091125, blue:0.5780913233757019, '
                'alpha:0.20609822869300842), directional_light_color: Rgba(red:0.8133212327957153, '
                'green:0.8235888481140137, blue:0.6534725427627563, alpha:0.16022956371307373), '
                'directional_light_exponent: 0.5206693410873413, falloff: "")',
 'Friction': '(coefficient: 0.5714026093482971, combine_rule: "")',
 'Frustum': '',
 'Fxaa': '(edge_threshold: "", edge_threshold_min: "", enabled: true)',
 'GlobalTransform': '((matrix3: (x_axis: Vec3A(x:0.5714026093482971, y:0.42888906598091125, z:0.5780913233757019), '
                    'y_axis: Vec3A(x:0.20609822869300842, y:0.8133212327957153, z:0.8235888481140137), z_axis: '
                    'Vec3A(x:0.6534725427627563, y:0.16022956371307373, z:0.5206693410873413)), translation: '
                    'Vec3A(x:0.3277728259563446, y:0.24999667704105377, z:0.952816903591156)))',
 'GltfExtras': '(value: "sbnpsago")',
 'GravityScale': '(0.5714026093482971)',
 'Group': '(73)',
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
 'Interaction': 'None',
 'Label': '',
 'LockedAxes': '(73)',
 'MaterialInfo': '(name: "sbnpsago", source: "piuzfbqp")',
 'Mesh2dHandle': '(Strong(""))',
 'MeshMorphWeights': '(weights: "")',
 'MorphWeights': '(first_mesh: "", weights: "")',
 'Name': '(hash: 73, name: "")',
 'NestedTupleStuff': '(0.5714026093482971, 54, (basic: (a: 0.4825616776943207, b: 1, c: "gopiuzfb"), color: '
                     '(Rgba(red:0.5206693410873413, green:0.3277728259563446, blue:0.24999667704105377, '
                     'alpha:0.952816903591156)), colors_list: ([Rgba(red:0.0445563830435276, green:0.8601610660552979, '
                     'blue:0.6031906008720398, alpha:0.38160598278045654), Rgba(red:0.2836182117462158, '
                     'green:0.6749648451805115, blue:0.456831157207489, alpha:0.6858614683151245)]), enable: true, '
                     'enum_inner: Rock, nested: (vec: (Vec3(x:0.1329781413078308, y:0.7678378224372864, '
                     'z:0.9824132323265076))), text: "otmbsahe", toggle: (false)))',
 'NestingTestLevel2': '(basic: (a: 0.5714026093482971, b: 54, c: "psagopiu"), color: (Rgba(red:0.8106188178062439, '
                      'green:0.03440357372164726, blue:0.49008557200431824, alpha:0.07608934491872787)), colors_list: '
                      '([Rgba(red:0.0445563830435276, green:0.8601610660552979, blue:0.6031906008720398, '
                      'alpha:0.38160598278045654), Rgba(red:0.2836182117462158, green:0.6749648451805115, '
                      'blue:0.456831157207489, alpha:0.6858614683151245)]), enable: true, enum_inner: Rock, nested: '
                      '(vec: (Vec3(x:0.1329781413078308, y:0.7678378224372864, z:0.9824132323265076))), text: '
                      '"otmbsahe", toggle: (false))',
 'NestingTestLevel3': '(vec: (Vec3(x:0.5714026093482971, y:0.42888906598091125, z:0.5780913233757019)))',
 'NoFrustumCulling': '',
 'NoWireframe': '',
 'Node': '(calculated_size: Vec2(x:0.5714026093482971, y:0.42888906598091125), outline_offset: 0.5780913233757019, '
         'outline_width: 0.20609822869300842, stack_index: 62, unrounded_size: Vec2(x:0.8235888481140137, '
         'y:0.6534725427627563))',
 'NotShadowCaster': '',
 'NotShadowReceiver': '',
 'OrthographicProjection': '(area: (max: Vec2(x:0.5714026093482971, y:0.42888906598091125), min: '
                           'Vec2(x:0.5780913233757019, y:0.20609822869300842)), far: 0.8133212327957153, near: '
                           '0.8235888481140137, scale: 0.6534725427627563, scaling_mode: '
                           'WindowSize(0.03440357372164726), viewport_origin: Vec2(x:0.49008557200431824, '
                           'y:0.07608934491872787))',
 'Outline': '(color: Rgba(red:0.5714026093482971, green:0.42888906598091125, blue:0.5780913233757019, '
            'alpha:0.20609822869300842), offset: VMax(0.4912964105606079), width: Percent(0.6534725427627563))',
 'Parent': '("")',
 'PerspectiveProjection': '(aspect_ratio: 0.5714026093482971, far: 0.42888906598091125, fov: 0.5780913233757019, near: '
                          '0.20609822869300842)',
 'Pickable': '',
 'Player': '',
 'PointLight': '(color: Rgba(red:0.5714026093482971, green:0.42888906598091125, blue:0.5780913233757019, '
               'alpha:0.20609822869300842), intensity: 0.8133212327957153, radius: 0.8235888481140137, range: '
               '0.6534725427627563, shadow_depth_bias: 0.16022956371307373, shadow_normal_bias: 0.5206693410873413, '
               'shadows_enabled: false)',
 'PrimaryWindow': '',
 'Projection': 'Perspective((aspect_ratio: 0.42888906598091125, far: 0.5780913233757019, fov: 0.20609822869300842, '
               'near: 0.8133212327957153))',
 'RelativeCursorPosition': '(normalized: "", normalized_visible_node_rect: (max: Vec2(x:0.5714026093482971, '
                           'y:0.42888906598091125), min: Vec2(x:0.5780913233757019, y:0.20609822869300842)))',
 'RenderLayers': '(73)',
 'Restitution': '(coefficient: 0.5714026093482971, combine_rule: "")',
 'RigidBody': 'Dynamic',
 'SSAOSettings': '',
 'ScreenSpaceAmbientOcclusionSettings': '(quality_level: "")',
 'Sensor': '',
 'ShadowFilteringMethod': 'Jimenez14',
 'ShadowmapSettings': '(size: 73)',
 'SkinnedMesh': '(inverse_bindposes: Strong(""), joints: [])',
 'Sleeping': '(angular_threshold: 0.5714026093482971, linear_threshold: 0.42888906598091125, sleeping: true)',
 'SolverGroups': '(filters: (73), memberships: (4))',
 'SpawnHere': '',
 'SpotLight': '(color: Rgba(red:0.5714026093482971, green:0.42888906598091125, blue:0.5780913233757019, '
              'alpha:0.20609822869300842), inner_angle: 0.8133212327957153, intensity: 0.8235888481140137, '
              'outer_angle: 0.6534725427627563, radius: 0.16022956371307373, range: 0.5206693410873413, '
              'shadow_depth_bias: 0.3277728259563446, shadow_normal_bias: 0.24999667704105377, shadows_enabled: true)',
 'Sprite': '(anchor: Custom(Vec2(x:0.03258506581187248, y:0.4825616776943207)), color: Rgba(red:0.014832446351647377, '
           'green:0.46258050203323364, blue:0.4912964105606079, alpha:0.27752065658569336), custom_size: "", flip_x: '
           'true, flip_y: false, rect: "")',
 'Style': '(align_content: SpaceAround, align_items: Default, align_self: Baseline, aspect_ratio: '
          'Some(0.5780913233757019), border: (bottom: Px(0.46258050203323364), left: Vw(0.8235888481140137), right: '
          'VMin(0.8106188178062439), top: Auto), bottom: Vh(0.49008557200431824), column_gap: Auto, direction: '
          'Inherit, display: None, flex_basis: Percent(0.0445563830435276), flex_direction: Column, flex_grow: '
          '0.6031906008720398, flex_shrink: 0.38160598278045654, flex_wrap: Wrap, grid_auto_columns: "", '
          'grid_auto_flow: RowDense, grid_auto_rows: "", grid_column: (end: "", span: "", start: ""), grid_row: (end: '
          '"", span: "", start: ""), grid_template_columns: "", grid_template_rows: "", height: '
          'Vw(0.17467059195041656), justify_content: FlexEnd, justify_items: Stretch, justify_self: End, left: '
          'Px(0.45692843198776245), margin: (bottom: VMax(0.9824132323265076), left: Vw(0.6133268475532532), right: '
          'Auto, top: Vh(0.004055144265294075)), max_height: Px(0.1949533075094223), max_width: '
          'Percent(0.5363451838493347), min_height: VMax(0.8981962203979492), min_width: Percent(0.666689932346344), '
          'overflow: (x: Clip, y: Clip), padding: (bottom: Vw(0.06499417871236801), left: Vh(0.32468828558921814), '
          'right: Vh(0.15641891956329346), top: Px(0.9697836637496948)), position_type: Relative, right: Auto, '
          'row_gap: Auto, top: Vw(0.3011642396450043), width: Vh(0.6578909158706665))',
 'Text': '(alignment: Right, linebreak_behavior: WordBoundary, sections: [(style: (color: Rgba(red:0.4825616776943207, '
         'green:0.014832446351647377, blue:0.46258050203323364, alpha:0.4912964105606079), font: Weak(Index(index: '
         '"")), font_size: 0.03440357372164726), value: "pkchxlbn"), (style: (color: Rgba(red:0.8601610660552979, '
         'green:0.6031906008720398, blue:0.38160598278045654, alpha:0.2836182117462158), font: Weak(Uuid(uuid: "")), '
         'font_size: 0.17467059195041656), value: "jvleoyho")])',
 'Text2dBounds': '(size: Vec2(x:0.5714026093482971, y:0.42888906598091125))',
 'TextFlags': '(needs_new_measure_func: true, needs_recompute: false)',
 'TextLayoutInfo': '(glyphs: "", logical_size: Vec2(x:0.5714026093482971, y:0.42888906598091125))',
 'TextureAtlasSprite': '(anchor: Custom(Vec2(x:0.03258506581187248, y:0.4825616776943207)), color: '
                       'Rgba(red:0.014832446351647377, green:0.46258050203323364, blue:0.4912964105606079, '
                       'alpha:0.27752065658569336), custom_size: "", flip_x: true, flip_y: false, index: 4)',
 'Tonemapping': 'None',
 'Transform': '(rotation: Quat(x:0.5714026093482971, y:0.42888906598091125, z:0.5780913233757019, '
              'w:0.20609822869300842), scale: Vec3(x:0.8133212327957153, y:0.8235888481140137, z:0.6534725427627563), '
              'translation: Vec3(x:0.16022956371307373, y:0.5206693410873413, z:0.3277728259563446))',
 'TupleTest2': '(0.5714026093482971, 54, "psagopiu")',
 'TupleTestBool': '(true)',
 'TupleTestColor': '(Rgba(red:0.5714026093482971, green:0.42888906598091125, blue:0.5780913233757019, '
                   'alpha:0.20609822869300842))',
 'TupleTestF32': '(0.5714026093482971)',
 'TupleTestStr': '("sbnpsago")',
 'TupleTestU64': '(73)',
 'TupleVec': '(["npsagopi"])',
 'TupleVec2': '(Vec2(x:0.5714026093482971, y:0.42888906598091125))',
 'TupleVec3': '(Vec3(x:0.5714026093482971, y:0.42888906598091125, z:0.5780913233757019))',
 'TupleVecF32F32': '([(0.42888906598091125, 0.5780913233757019)])',
 'UiCameraConfig': '(show_ui: true)',
 'UiImage': '(flip_x: true, flip_y: false, texture: Weak(Uuid(uuid: "")))',
 'UiImageSize': '(size: Vec2(x:0.5714026093482971, y:0.42888906598091125))',
 'UiTextureAtlasImage': '(flip_x: true, flip_y: false, index: 54)',
 'UnitTest': '',
 'VecOfColors': '([Rgba(red:0.42888906598091125, green:0.5780913233757019, blue:0.20609822869300842, '
                'alpha:0.8133212327957153)])',
 'VecOfVec3s2': '([(Vec3(x:0.42888906598091125, y:0.5780913233757019, z:0.20609822869300842))])',
 'Velocity': '(angvel: Vec3(x:0.5714026093482971, y:0.42888906598091125, z:0.5780913233757019), linvel: '
             'Vec3(x:0.20609822869300842, y:0.8133212327957153, z:0.8235888481140137))',
 'ViewVisibility': '(true)',
 'Visibility': 'Visible',
 'VisibleEntities': '',
 'Window': '(canvas: None, composite_alpha_mode: PostMultiplied, cursor: (grab_mode: Confined, hit_test: true, icon: '
           'Default, visible: false), decorations: false, enabled_buttons: (close: true, maximize: false, minimize: '
           'true), fit_canvas_to_parent: false, focused: true, ime_enabled: true, ime_position: '
           'Vec2(x:0.16022956371307373, y:0.5206693410873413), internal: (maximize_request: Some(false), '
           'minimize_request: None, physical_cursor_position: Some(DVec2(x:0.0445563830435276, '
           'y:0.8601610660552979))), mode: SizedFullscreen, position: Centered(Primary), present_mode: Fifo, '
           'prevent_default_event_handling: true, resizable: true, resize_constraints: (max_height: '
           '0.2623211145401001, max_width: 0.17467059195041656, min_height: 0.30310511589050293, min_width: '
           '0.36258742213249207), resolution: (physical_height: 58, physical_width: 98, scale_factor: '
           '0.8600491285324097, scale_factor_override: None), title: "otmbsahe", transparent: false, visible: true, '
           'window_level: Normal, window_theme: "")',
 'Wireframe': '',
 'ZIndex': 'Local(54)'}


def test_components_should_generate_correct_custom_properties_with_randomozied_values():
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

    pp = pprint.PrettyPrinter(depth=14, width=120)
    print("CUSTOM PROPERTY VALUES")
    pp.pprint(custom_property_values)

    assert len(errors) == 0
    assert len(added_components) == 150

def _test_components_should_generate_correct_propertyGroup_values_from_custom_properties():
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
    failing_components = []

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
            added_components.append(component_type)

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
            failing_components.append(short_name)

    print("ERRRORS")
    for index, error in enumerate(errors):
        print("ERROR", error, failing_components[index])
    assert len(errors) == 1
    assert len(added_components) == 150


def _test_remove_components():
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
    
def _test_copy_paste_components():
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

