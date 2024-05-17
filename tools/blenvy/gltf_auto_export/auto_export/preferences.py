
import os
from bpy.types import AddonPreferences
from bpy.props import (BoolProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

AutoExportGltfPreferenceNames = [
    'will_save_settings',
    'direct_mode',# specific to main auto_export operator

    'show_general_settings',
    'auto_export',
    'project_root_path',
    'assets_path',
    'export_scene_settings',

    'show_change_detection_settings',
    'change_detection',

    'show_scene_settings',
    'main_scenes',
    'library_scenes',
    'main_scenes_index',
    'library_scenes_index',
    'main_scene_names',
    'library_scene_names',

    'show_blueprint_settings',
    'export_blueprints',
    'blueprints_path',
    'export_marked_assets',
    'collection_instances_combine_mode',

    'levels_path',
    'export_separate_dynamic_and_static_objects',

    'export_materials_library',
    'materials_path',
]

def on_export_output_folder_updated(self, context):
    #self.project_root_path = os.path.relpath(self.project_root_path)
    #self.assets_path = os.path.join(self.project_root_path, self.assets_path)
    print("on_foo_updated", self.project_root_path, self.assets_path)

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
    ) # type: ignore
    
    # use when operator is called directly, works a bit differently than inside the ui
    direct_mode: BoolProperty(
        default=False
    ) # type: ignore


    auto_export: BoolProperty(
        name='Auto export',
        description='Automatically export to gltf on save',
        default=False
    ) # type: ignore

    #### general
    # for UI only, workaround for lacking panels
    show_general_settings: BoolProperty(
        name="show_general settings",
        description="show/hide general settings (UI only: has no impact on exports)",
        default=True
    ) # type: ignore

    project_root_path: StringProperty(
        name = "Project Root Path",
        description="The root folder of your (Bevy) project (not assets!)",
        # subtype='DIR_PATH',
        default='../'
        #update=on_export_output_folder_updated) # type: ignore
    )
    
    assets_path: StringProperty(
        name='Export folder',
        description='The root folder for all exports(relative to the root folder/path) Defaults to "assets" ',
        default='./assets',
        #subtype='DIR_PATH',
        options={'HIDDEN'}
        # update=on_export_output_folder_updated
    ) # type: ignore

    # for UI only, workaround for lacking panels
    show_change_detection_settings: BoolProperty(
        name="show change detection settings",
        description="show/hide change detection settings (UI only: has no impact on exports)",
        default=True
    ) # type: ignore 

    change_detection: BoolProperty(
        name='Change detection',
        description='Use change detection to determine what/if should be exported',
        default=True
    ) # type: ignore

    # scenes 
    # for UI only, workaround for lacking panels
    show_scene_settings: BoolProperty(
        name="show scene settings",
        description="show/hide scene settings (UI only: has no impact on exports)",
        default=True
    ) # type: ignore 

    # scene components
    export_scene_settings: BoolProperty(
        name='Export scene settings',
        description='Export scene settings ie AmbientLighting, Bloom, AO etc',
        default=False
    ) # type: ignore

    # blueprint settings
    # for UI only, workaround for lacking panels
    show_blueprint_settings: BoolProperty(
        name="show blueprint settings",
        description="show/hide blueprint settings (UI only: has no impact on exports)",
        default=True
    ) # type: ignore

    export_blueprints: BoolProperty(
        name='Export Blueprints',
        description='Replaces collection instances with an Empty with a BlueprintName custom property, and enabled a lot more features !',
        default=True
    ) # type: ignore

    blueprints_path: StringProperty(
        name='Blueprints path',
        description='path to export the blueprints to (relative to the assets folder)',
        default='blueprints',
        #subtype='DIR_PATH'
    ) # type: ignore

    levels_path: StringProperty(
        name='Levels path',
        description='path to export the levels (main scenes) to (relative to the assets folder)',
        default='levels',
        #subtype='DIR_PATH'
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

    materials_path: StringProperty(
        name='Materials path',
        description='path to export the materials libraries to (relative to the assets folder)',
        default='materials',
        #subtype='DIR_PATH'
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

