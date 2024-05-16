import bpy
from ...settings import load_settings

######################################################

## ui logic & co
def draw_folder_browser(layout, label, prop_origin, target_property):
    row = layout.row()
    row.label(text=label)

    '''box = row.box()
    box.scale_y = 0.5
    box.label(text=value)'''

    col = row.column()
    col.enabled = False
    col.prop(prop_origin, target_property, text="")

    folder_selector = row.operator("generic.open_folderbrowser", icon="FILE_FOLDER", text="")
    folder_selector.target_property = target_property #"export_root_path"

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

        current_auto_settings = load_settings(".gltf_auto_export_settings")
        current_gltf_settings = load_settings(".gltf_auto_export_gltf_settings")
        
        if current_auto_settings is not None:
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

        if blenvy.mode == "SETTINGS":
            header, panel = layout.panel("auto_export", default_closed=False)
            header.label(text="Common")
            if panel:
                row = panel.row()
                draw_folder_browser(layout=row, label="Root Folder", prop_origin=blenvy, target_property="export_root_path")
                row = panel.row()
                draw_folder_browser(layout=row, label="Assets Folder", prop_origin=blenvy, target_property="export_assets_path")
                row = panel.row()
                draw_folder_browser(layout=row, label="Blueprints Folder", prop_origin=blenvy, target_property="export_blueprints_path")
                row = panel.row()
                draw_folder_browser(layout=row, label="Levels Folder", prop_origin=blenvy, target_property="export_levels_path")
                row = panel.row()
                draw_folder_browser(layout=row, label="Materials Folder", prop_origin=blenvy, target_property="export_materials_path")

                panel.separator()
                # scenes selection
                section = panel
                rows = 2
                row = section.row()
                row.label(text="main scenes")
                row.prop(context.window_manager, "main_scene", text='')

                row = section.row()
                row.template_list("SCENE_UL_Blenvy", "level scenes", blenvy, "main_scenes", blenvy, "main_scenes_index", rows=rows)

                col = row.column(align=True)
                sub_row = col.row()
                add_operator = sub_row.operator("scene_list.list_action", icon='ADD', text="")
                add_operator.action = 'ADD'
                add_operator.scene_type = 'level'
                #add_operator.operator = operator
                sub_row.enabled = context.window_manager.main_scene is not None

                sub_row = col.row()
                remove_operator = sub_row.operator("scene_list.list_action", icon='REMOVE', text="")
                remove_operator.action = 'REMOVE'
                remove_operator.scene_type = 'level'
                col.separator()

                # library scenes
                row = section.row()
                row.label(text="library scenes")
                row.prop(context.window_manager, "library_scene", text='')

                row = section.row()
                row.template_list("SCENE_UL_Blenvy", "library scenes", blenvy, "library_scenes", blenvy, "library_scenes_index", rows=rows)

                col = row.column(align=True)
                sub_row = col.row()
                add_operator = sub_row.operator("scene_list.list_action", icon='ADD', text="")
                add_operator.action = 'ADD'
                add_operator.scene_type = 'library'
                sub_row.enabled = context.window_manager.library_scene is not None


                sub_row = col.row()
                remove_operator = sub_row.operator("scene_list.list_action", icon='REMOVE', text="")
                remove_operator.action = 'REMOVE'
                remove_operator.scene_type = 'library'
                col.separator()

              
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


