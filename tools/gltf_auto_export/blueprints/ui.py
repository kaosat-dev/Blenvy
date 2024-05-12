import bpy 

class GLTF_PT_auto_export_blueprints_list(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Blueprints"
    bl_parent_id = "GLTF_PT_auto_export_SidePanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        for blueprint in context.window_manager.blueprints_registry.blueprints_list:
            row = layout.row()
            row.label(text=blueprint.name)

            if blueprint.local:
                select_blueprint = row.operator(operator="blueprint.select", text="Select")
                select_blueprint.blueprint_collection_name = blueprint.collection.name
                select_blueprint.blueprint_scene_name = blueprint.scene.name
            else:
                row.label(text="External")

        for collection in bpy.context.window_manager.exportedCollections:
            row = layout.row()
            row.label(text=collection.name)