import bpy
from .helpers import make_empty3
# helpers to export scene level data

def upsert_scene_components(scene, world):
    
    lighting_components = None
    for object in scene.objects:
        if object.name == "lighting_components":
            lighting_components = object
            break

    if lighting_components is None:
        lighting_components = make_empty3('lighting_components', [0,0,0], [0,0,0], [0,0,0], None)

    lighting_components['AmbientLightP'] = ambient_color_to_component(world)

def ambient_color_to_component(world):
    color = None
    strength = None
    try:
        color = world.node_tree.nodes['Background'].inputs[0].default_value
        strength = world.node_tree.nodes['Background'].inputs[1].default_value
    except Exception as ex:
        print("failed to parse ambient color: Only backgroud is supported")
   

    if color is not None and strength is not None:
        #print("color", color[0], color[1], color[2], color[3])
        # print("strength", strength)

        colorRgba = "Rgba(red: "+ str(color[0]) + ", green: "+ str(color[1]) + ", blue: " + str(color[2]) + ", alpha: "+ str(color[3]) + ")" # TODO: YIKES clean this up
        #colorRgba = "Rgba(red: 0.0, green: 0.0, blue:0.0, alpha:0.0)"
        component = "( color:"+ str(colorRgba)  +", brightness:"+str(strength)+")"

        print("component", component)
        return component
    return None

def rendering(render):
    bpy.context.scene.render
    bpy.context.scene.eevee.use_bloom = True
