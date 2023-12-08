bl_info = {
    "name": "bevy_blueprints",
    "author": "kaosigh",
    "version": (0, 0, 1),
    "blender": (3, 4, 0),
    "location": "VIEW_3D",
    "description": "UI to help create Bevy blueprints and components",
    "warning": "",
    "wiki_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow",
    "tracker_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow/issues/new",
    "category": "User Interface"
}
import bpy

class BEVY_BLUEPRINTS_PT_TestPanel(bpy.types.Panel):
    bl_idname = "BEVY_BLUEPRINTS_PT_TestPanel"
    bl_label = "Bevy Components"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.label(text="How cool is this!AUTO_export"  )


classes = [
    BEVY_BLUEPRINTS_PT_TestPanel    
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
