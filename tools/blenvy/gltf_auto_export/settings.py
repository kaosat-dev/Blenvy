import bpy
from bpy_types import (PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty)

class AutoExportSettings(PropertyGroup):
    auto_export: BoolProperty(
        name='Auto export',
        description='Automatically export to gltf on save',
        default=False
    ) # type: ignore

    #### general
    change_detection: BoolProperty(
        name='Change detection',
        description='Use change detection to determine what/if should be exported',
        default=True
    ) # type: ignore

    # scenes 

    # scene components
    export_scene_settings: BoolProperty(
        name='Export scene settings',
        description='Export scene settings ie AmbientLighting, Bloom, AO etc',
        default=False
    ) # type: ignore

    # blueprint settings
    export_blueprints: BoolProperty(
        name='Export Blueprints',
        description='Replaces collection instances with an Empty with a BlueprintName custom property, and enabled a lot more features !',
        default=True
    ) # type: ignore

    export_separate_dynamic_and_static_objects: BoolProperty(
        name="Export levels' dynamic and static objects seperatly",
        description="""For MAIN scenes only (aka levels), toggle this to generate 2 files per level: 
            - one with all dynamic data: collection or instances marked as dynamic/ saveable
            - one with all static data: anything else that is NOT marked as dynamic""",
        default=False
    ) # type: ignore

    export_materials_library: BoolProperty(
        name='Export materials library',
        description='remove materials from blueprints and use the material library instead',
        default=False
    ) # type: ignore


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
    ) # type: ignore

    export_marked_assets: BoolProperty(
        name='Auto export marked assets',
        description='Collections that have been marked as assets will be systematically exported, even if not in use in another scene',
        default=True
    ) # type: ignore
