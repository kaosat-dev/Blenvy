import bpy
import json

######################################################
## ui logic & co

# side panel
class BLENVY_PT_SidePanel(bpy.types.Panel):
    bl_idname = "BLENVY_PT_SidePanel"
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy"
    bl_context = "objectmode"


    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Blenvy")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        blenvy = context.window_manager.blenvy
        active_mode = blenvy.mode
        world_scene_active = False
        library_scene_active = False
        active_collection = context.collection

        current_auto_settings = bpy.data.texts[".gltf_auto_export_settings"] if ".gltf_auto_export_settings" in bpy.data.texts else None
        current_gltf_settings = bpy.data.texts[".gltf_auto_export_gltf_settings"] if ".gltf_auto_export_gltf_settings" in bpy.data.texts else None

        if current_auto_settings is not None:
            current_auto_settings = json.loads(current_auto_settings.as_string())
            #print("current_auto_settings", current_auto_settings)
            main_scene_names = current_auto_settings["main_scene_names"]
            library_scene_names = current_auto_settings["library_scene_names"]

            world_scene_active = context.scene.name in main_scene_names
            library_scene_active = context.scene.name in library_scene_names


        # Now to actual drawing of the UI
        target = row.box() if active_mode == 'COMPONENTS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="PROPERTIES")
        tool_switch_components.tool = "COMPONENTS"

        target = row.box() if active_mode == 'BLUEPRINTS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="PACKAGE")
        tool_switch_components.tool = "BLUEPRINTS"

        target = row.box() if active_mode == 'ASSETS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="ASSET_MANAGER")
        tool_switch_components.tool = "ASSETS"

        target = row.box() if active_mode == 'SETTINGS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="SETTINGS")
        tool_switch_components.tool = "SETTINGS"

        target = row.box() if active_mode == 'TOOLS' else row
        tool_switch_components = target.operator(operator="bevy.tooling_switch", text="", icon="TOOL_SETTINGS")
        tool_switch_components.tool = "TOOLS"

        # Debug stuff
        """layout.label(text="Active Blueprint: "+ active_collection.name.upper())
        layout.label(text="World scene active: "+ str(world_scene_active))
        layout.label(text="Library scene active: "+ str(library_scene_active))
        layout.label(text=blenvy.mode)"""

        """if blenvy.mode == "SETTINGS":
            header, panel = layout.panel("auto_export", default_closed=False)
            header.label(text="Auto Export")
            if panel:
                layout = panel
                layout.label(text="MAKE SURE TO KEEP 'REMEMBER EXPORT SETTINGS' TOGGLED !!")
                op = layout.operator("EXPORT_SCENE_OT_gltf", text='Gltf Settings')#'glTF 2.0 (.glb/.gltf)')
                #op.export_format = 'GLTF_SEPARATE'
                op.use_selection=True
                op.will_save_settings=True
                op.use_visible=True # Export visible and hidden objects. See Object/Batch Export to skip.
                op.use_renderable=True
                op.use_active_collection = True
                op.use_active_collection_with_nested=True
                op.use_active_scene = True
                op.filepath="____dummy____"
                op.gltf_export_id = "gltf_auto_export" # we specify that we are in a special case

                op = layout.operator("EXPORT_SCENES_OT_auto_gltf", text="Auto Export Settings")
                op.auto_export = True"""

        """header, panel = layout.panel("components", default_closed=False)
        header.label(text="Components")
        if panel:
            panel.label(text="YOOO")"""


