from typing import Set
import bpy
######################################################
## ui logic & co

# side panel that opens auto_export specific gltf settings & the auto export settings themselves
class GLTF_PT_auto_export_SidePanel(bpy.types.Panel):
    bl_idname = "GLTF_PT_auto_export_SidePanel"
    bl_label = "Auto export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Auto Export"
    bl_context = "objectmode"
    bl_parent_id = "BLENVY_PT_SidePanel"

    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'SETTINGS'
    
    """def draw_header(self, context):
        layout = self.layout
        layout.label(text="Auto export ")"""

    def draw(self, context):
        layout = self.layout
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
        op.auto_export = True

# main ui in the file => export 
class GLTF_PT_auto_export_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = ""
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

class GLTF_PT_auto_export_root(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Auto export"
    bl_parent_id = "GLTF_PT_auto_export_main"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf"

    def draw_header(self, context):
        sfile = context.space_data
        operator = sfile.active_operator
        self.layout.prop(operator, "auto_export", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.active = operator.auto_export
        layout.prop(operator, 'will_save_settings')
        
class GLTF_PT_auto_export_general(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "General"
    bl_parent_id = "GLTF_PT_auto_export_root"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf" #"EXPORT_SCENE_OT_gltf"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.active = operator.auto_export
        layout.prop(operator, "export_assets_path")
        layout.prop(operator, "export_scene_settings")


class GLTF_PT_auto_export_change_detection(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Change detection"
    bl_parent_id = "GLTF_PT_auto_export_root"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf" #"EXPORT_SCENE_OT_gltf"
    def draw_header(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator
        layout.prop(operator, "export_change_detection", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.active = operator.auto_export
        layout.prop(operator, "export_change_detection")

class GLTF_PT_auto_export_blueprints(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Blueprints"
    bl_parent_id = "GLTF_PT_auto_export_root"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENES_OT_auto_gltf" #"EXPORT_SCENE_OT_gltf"


    def draw_header(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator
        layout.prop(operator, "export_blueprints", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.active = operator.auto_export and operator.export_blueprints
                 
         # collections/blueprints 
        layout.prop(operator, "export_blueprints_path")
        layout.prop(operator, "collection_instances_combine_mode")
        layout.prop(operator, "export_marked_assets")
        layout.prop(operator, "export_separate_dynamic_and_static_objects")
        layout.separator()
        # materials
        layout.prop(operator, "export_materials_library")
        layout.prop(operator, "export_materials_path")
   