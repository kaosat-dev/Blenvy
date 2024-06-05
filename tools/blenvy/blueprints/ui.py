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
        return context.window_manager.blenvy.mode == 'BLUEPRINTS' if 'blenvy' in context.window_manager else False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        asset_registry = context.window_manager.assets_registry
        blueprint_registry = context.window_manager.blueprints_registry

        blueprint_registry.refresh_blueprints()

        for blueprint in blueprint_registry.blueprints_data.blueprints:

            header, panel = layout.box().panel(f"blueprint_assets{blueprint.name}", default_closed=True)
            if header:
                header.label(text=blueprint.name)
                header.prop(blueprint.collection, "always_export")
                
                if blueprint.local:
                    select_blueprint = header.operator(operator="blueprint.select", text="", icon="RESTRICT_SELECT_OFF")
                    if blueprint.collection and blueprint.collection.name:
                        select_blueprint.blueprint_collection_name = blueprint.collection.name
                    select_blueprint.blueprint_scene_name = blueprint.scene.name

            if panel:
                split  = panel.split(factor=0.005)
                col = split.column()
                col.label(text=" ")

                col = split.column()

                if blueprint.local:
                    user_assets = get_user_assets(blueprint.collection)
                    draw_assets(layout=col, name=blueprint.name, title="Assets", asset_registry=asset_registry, user_assets=user_assets, target_type="BLUEPRINT", target_name=blueprint.name)

                else:
                    assets = get_user_assets(blueprint.collection)
                    draw_assets(layout=col, name=blueprint.name, title="Assets", asset_registry=asset_registry, user_assets=user_assets, target_type="BLUEPRINT", target_name=blueprint.name, editable=False)
                    panel.label(text="External")