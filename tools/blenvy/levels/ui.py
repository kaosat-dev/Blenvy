from types import SimpleNamespace
import bpy
from ..assets.assets_scan import get_main_scene_assets_tree
from ..assets.asset_helpers import get_user_assets
from ..assets.ui import draw_assets

class Blenvy_levels(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ""
    bl_parent_id = "BLENVY_PT_SidePanel"
    bl_options = {'DEFAULT_CLOSED','HIDE_HEADER'}
    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'LEVELS'
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        blenvy = context.window_manager.blenvy
        layout.operator(operator="bevyassets.test")

        asset_registry = context.window_manager.assets_registry
        blueprints_registry = context.window_manager.blueprints_registry
        #blueprints_registry.refresh_blueprints()
        blueprints_data = blueprints_registry.blueprints_data

        for scene_selector in blenvy.main_scenes:
            scene = bpy.data.scenes[scene_selector.name]
            header, panel = layout.box().panel(f"assets{scene.name}", default_closed=False)
            if header:
                header.label(text=scene.name, icon="HIDE_OFF")
                header.prop(scene, "always_export")
                select_level = header.operator(operator="level.select", text="", icon="RESTRICT_SELECT_OFF")
                select_level.level_name = scene.name

            if panel:
                user_assets = get_user_assets(scene)
                row = panel.row()
                #row.label(text="row")
                """col = row.column()
                col.label(text=" ")

                col = row.column()
                col.label(text="col in row 2")

                column = panel.column()
                column.label(text="col")"""

                split  = panel.split(factor=0.005)
                col = split.column()
                col.label(text=" ")

                col = split.column()
                #col.label(text="col in row 2")

                scene_assets_panel = draw_assets(layout=col, name=f"{scene.name}_assets", title=f"Assets", asset_registry=asset_registry, user_assets=user_assets, target_type="SCENE", target_name=scene.name)

    
        settings = {"blueprints_path": "blueprints", "export_gltf_extension": ".glb"}
        settings = SimpleNamespace(**settings)

        """if panel:
            for scene_selector in blenvy.main_scenes:
                scene = bpy.data.scenes[scene_selector.name]
                #get_main_scene_assets_tree(scene, blueprints_data, settings)
                user_assets = get_user_assets(scene)
                #print("user assets", user_assets, scene)
                row = panel.row()
                header.prop(scene, "always_export")

                sub_header, sub_panel = row.box().panel(f"assets{name}", default_closed=False)


                scene_assets_panel = draw_assets(layout=sub_panel, name=scene.name, title=f"{scene.name} Assets", asset_registry=asset_registry, user_assets=user_assets, target_type="SCENE", target_name=scene.name)
                """