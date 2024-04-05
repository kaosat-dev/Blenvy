
from bpy.types import AddonPreferences

from bpy.props import (BoolProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

from .internals import (CUSTOM_PG_sceneName)

AutoExportGltfPreferenceNames = [
    'auto_export',
    'export_main_scene_name',
    'export_output_folder',
    'export_library_scene_name',
    'export_change_detection',

    'export_blueprints',
    'export_blueprints_path',

    'export_marked_assets',
    'collection_instances_combine_mode',
    'export_separate_dynamic_and_static_objects',
    'export_legacy_mode',

    'export_materials_library',
    'export_materials_path',

    'export_scene_settings',

    'main_scenes',
    'library_scenes',
    'main_scenes_index',
    'library_scenes_index',

    'direct_mode',# specific to main auto_export operator
    'main_scene_names',
    'library_scene_names',
    'previous_export_settings',
    'will_save_settings',
]

class AutoExportGltfAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__
    bl_options = {'PRESET'}

    #### these are for the operator
    will_save_settings: BoolProperty(
        name='Remember Export Settings',
        description='Store glTF export settings in the Blender project',
        default=True
    )
    
    # use when operator is called directly, works a bit differently than inside the ui
    direct_mode: BoolProperty(
        default=False
    )

    ####
    auto_export: BoolProperty(
        name='Auto export',
        description='Automatically export to gltf on save',
        default=False
    )
    export_main_scene_name: StringProperty(
        name='Main scene',
        description='The name of the main scene/level/world to auto export',
        default='Scene'
    )
    export_output_folder: StringProperty(
        name='Export folder (relative)',
        description='The root folder for all exports(relative to current file) Defaults to current folder',
        default=''
    )
    export_library_scene_name: StringProperty(
        name='Library scene',
        description='The name of the library scene to auto export',
        default='Library'
    )
    export_change_detection: BoolProperty(
        name='Change detection',
        description='Use change detection to determine what/if should be exported',
        default=True
    )
    # scene components
    export_scene_settings: BoolProperty(
        name='Export scene settings',
        description='Export scene settings ie AmbientLighting, Bloom, AO etc',
        default=False
    )

    # blueprint settings
    export_blueprints: BoolProperty(
        name='Export Blueprints',
        description='Replaces collection instances with an Empty with a BlueprintName custom property',
        default=True
    )
    export_blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to the Export folder)',
        default='library'
    )

    export_materials_library: BoolProperty(
        name='Export materials library',
        description='remove materials from blueprints and use the material library instead',
        default=False
    )
    export_materials_path: StringProperty(
        name='Materials path',
        description='path to export the materials libraries to (relative to the root folder)',
        default='materials'
    )

    """ combine mode can be 
              - 'Split' (default): replace with an empty, creating links to sub blueprints 
              - 'Embed' : treat it as an embeded object and do not replace it with an empty
              - 'EmbedExternal': embed any instance of a non local collection (ie external assets)

              - 'Inject': inject components from sub collection instances into the curent object => this is now a seperate custom property that you can apply to a collecion instance
            """

    collection_instances_combine_mode : EnumProperty(
        name='Collection instances',
        items=(
           ('Split', 'Split', 'replace collection instances with an empty + blueprint, creating links to sub blueprints (Default, Recomended)'),
           ('Embed', 'Embed', 'treat collection instances as embeded objects and do not replace them with an empty'),
           ('EmbedExternal', 'EmbedExternal', 'treat instances of external (not specifified in the current blend file) collections (aka assets etc) as embeded objects and do not replace them with empties'),
           #('Inject', 'Inject', 'inject components from sub collection instances into the curent object')
        ),
        default='Split'
    )

    export_marked_assets: BoolProperty(
        name='Auto export marked assets',
        description='Collections that have been marked as assets will be systematically exported, even if not in use in another scene',
        default=True
    )

    export_separate_dynamic_and_static_objects: BoolProperty(
        name='Export dynamic and static objects seperatly',
        description="""For MAIN scenes only (aka levels), toggle this to generate 2 files per level: 
            - one with all dynamic data: collection or instances marked as dynamic/ saveable
            - one with all static data: anything else that is NOT marked as dynamic""",
        default=False
    )

    export_legacy_mode: BoolProperty(
        name='Legacy mode for Bevy',
        description='Toggle this if you want to be compatible with bevy_gltf_blueprints/components < 0.8',
        default=True
    )

    main_scenes: CollectionProperty(name="main scenes", type=CUSTOM_PG_sceneName)
    main_scenes_index: IntProperty(name = "Index for main scenes list", default = 0)

    library_scenes: CollectionProperty(name="library scenes", type=CUSTOM_PG_sceneName)
    library_scenes_index: IntProperty(name = "Index for library scenes list", default = 0)
