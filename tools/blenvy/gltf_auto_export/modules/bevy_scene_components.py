
import bpy
from ...core.object_makers import make_empty

# TODO: replace this with placing scene level custom properties once support for that has been added to bevy_gltf
def upsert_scene_components(main_scenes):
    for scene in main_scenes:
        lighting_components_name = f"lighting_components_{scene.name}"
        lighting_components = bpy.data.objects.get(lighting_components_name, None)
        if not lighting_components:
            root_collection = scene.collection
            lighting_components = make_empty('lighting_components_'+scene.name, [0,0,0], [0,0,0], [0,0,0], root_collection)

        if scene.world is not None:
            lighting_components['BlenderBackgroundShader'] = ambient_color_to_component(scene.world)
        lighting_components['BlenderShadowSettings'] = scene_shadows_to_component(scene)

        if scene.eevee.use_bloom:
            lighting_components['BloomSettings'] = scene_bloom_to_component(scene)
        elif 'BloomSettings' in lighting_components:
            del lighting_components['BloomSettings']

        if scene.eevee.use_gtao: 
            lighting_components['SSAOSettings'] = scene_ao_to_component(scene)
        elif 'SSAOSettings' in lighting_components:
            del lighting_components['SSAOSettings']

def remove_scene_components(main_scenes):
    for scene in main_scenes:
        lighting_components_name = f"lighting_components_{scene.name}"
        lighting_components = bpy.data.objects.get(lighting_components_name, None)
        if lighting_components:
            bpy.data.objects.remove(lighting_components, do_unlink=True)


def ambient_color_to_component(world):
    color = None
    strength = None
    try:
        color = world.node_tree.nodes['Background'].inputs[0].default_value
        strength = world.node_tree.nodes['Background'].inputs[1].default_value
    except Exception as ex:
        print("failed to parse ambient color: Only background is supported")
   

    if color is not None and strength is not None:
        colorRgba = f"Rgba(red: {color[0]}, green: {color[1]}, blue: {color[2]}, alpha: {color[3]})"
        component = f"( color: {colorRgba}, strength: {strength})"
        return component
    return None

def scene_shadows_to_component(scene):
    cascade_size = scene.eevee.shadow_cascade_size
    component = f"(cascade_size: {cascade_size})"
    return component

def scene_bloom_to_component(scene):
    component = f"BloomSettings(intensity: {scene.eevee.bloom_intensity})"
    return component

def scene_ao_to_component(scene):
    ssao = scene.eevee.use_gtao
    component= "SSAOSettings()"
    return component