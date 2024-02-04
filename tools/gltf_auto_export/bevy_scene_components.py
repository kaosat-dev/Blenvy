
from .auto_export.object_makers import make_empty

def upsert_scene_components(scene, world, main_scene_names):
    #should only be run in one of the main scenes
    if scene.name not in main_scene_names:
        return
    root_collection = scene.collection
    lighting_components = None
    print("upsert scene components", scene.name, scene.objects)
    for object in scene.objects:
        if object.name == "lighting_components_"+scene.name:
            lighting_components = object
            break

    if lighting_components is None:
        lighting_components = make_empty('lighting_components_'+scene.name, [0,0,0], [0,0,0], [0,0,0], root_collection)

    if world is not None:
        lighting_components['AmbientLightSettings'] = ambient_color_to_component(world)

    lighting_components['ShadowmapSettings'] = scene_shadows_to_component(scene)


    if scene.eevee.use_bloom:
        lighting_components['BloomSettings'] = scene_bloom_to_component(scene)
    elif 'BloomSettings' in lighting_components:
        del lighting_components['BloomSettings']

    if scene.eevee.use_gtao: 
        lighting_components['SSAOSettings'] = scene_ao_to_component(scene)
    elif 'SSAOSettings' in lighting_components:
        del lighting_components['SSAOSettings']


def ambient_color_to_component(world):
    color = None
    strength = None
    try:
        color = world.node_tree.nodes['Background'].inputs[0].default_value
        strength = world.node_tree.nodes['Background'].inputs[1].default_value
    except Exception as ex:
        print("failed to parse ambient color: Only backgroud is supported")
   

    if color is not None and strength is not None:
        colorRgba = "Rgba(red: "+ str(color[0]) + ", green: "+ str(color[1]) + ", blue: " + str(color[2]) + ", alpha: "+ str(color[3]) + ")" # TODO: YIKES clean this up
        component = "( color:"+ str(colorRgba)  +", brightness:"+str(strength)+")"
        return component
    return None

def scene_shadows_to_component(scene):
    cascade_resolution = scene.eevee.shadow_cascade_size
    component = "(size: "+ cascade_resolution +")"
    return component

def scene_bloom_to_component(scene):
    component = "BloomSettings(intensity: "+ str(scene.eevee.bloom_intensity) +")"
    return component

def scene_ao_to_component(scene):
    ssao = scene.eevee.use_gtao
    component= "SSAOSettings()"
    return component