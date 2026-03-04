

def match_blender_visuals_in_bevy(match_blender_visuals):
    # inject/ update scene components
    upsert_scene_components(settings.level_scenes)

    #inject/ update light shadow information
    for light in bpy.data.lights:
        enabled = 'true' if light.use_shadow else 'false'
        # TODO: directly set relevant components instead ?
        light['BlenderLightShadows'] = f"(enabled: {enabled}, buffer_bias: {light.shadow_buffer_bias})"