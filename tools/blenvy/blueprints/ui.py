import bpy 
import json

from ..assets.asset_helpers import get_user_assets

from ..assets.ui import draw_assets

class GLTF_PT_auto_export_blueprints_list(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Blueprints"
    bl_parent_id = "BLENVY_PT_SidePanel"
    bl_options = {'DEFAULT_CLOSED','HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'BLUEPRINTS'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        asset_registry = context.window_manager.assets_registry

        for blueprint in context.window_manager.blueprints_registry.blueprints_list:
            row = layout.row()
            row.label(icon="RIGHTARROW")
            row.label(text=blueprint.name)

            if blueprint.local:
                
                select_blueprint = row.operator(operator="blueprint.select", text="", icon="RESTRICT_SELECT_OFF")
                
                if blueprint.collection and blueprint.collection.name:
                    select_blueprint.blueprint_collection_name = blueprint.collection.name
                select_blueprint.blueprint_scene_name = blueprint.scene.name

                user_assets = get_user_assets(blueprint.collection)
                draw_assets(layout=layout, name=blueprint.name, title="Assets", asset_registry=asset_registry, user_assets=user_assets, target_type="BLUEPRINT", target_name=blueprint.name)

            else:
                assets = get_user_assets(blueprint.collection)
                draw_assets(layout=layout, name=blueprint.name, title="Assets", asset_registry=asset_registry, user_assets=user_assets, target_type="BLUEPRINT", target_name=blueprint.name, editable=False)
                row.label(text="External")
