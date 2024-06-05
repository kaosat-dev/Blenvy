from types import SimpleNamespace
import bpy
from .assets_scan import get_main_scene_assets_tree
from .asset_helpers import get_user_assets, does_asset_exist

def draw_assets(layout, name, title, asset_registry, target_type, target_name, editable=True, user_assets= [], generated_assets = []):
    header, panel = layout.panel(f"assets{name}", default_closed=False)
    header.label(text=title, icon="ASSET_MANAGER")

    if panel:
        if editable:
            row = panel.row()
            blueprint_assets = target_type == 'BLUEPRINT'
            if blueprint_assets:
                target = bpy.data.collections[target_name]
            else:
                target = bpy.data.scenes[target_name]

            add_possible = does_asset_exist(target, {"path": asset_registry.asset_path_selector}) #"name": asset_registry.asset_name_selector, 

            row.alert = add_possible
            row.prop(asset_registry, "asset_name_selector", text="")
            row.label(text=asset_registry.asset_path_selector)
            asset_selector = row.operator(operator="asset.open_filebrowser", text="", icon="FILE_FOLDER")
            
            add_asset_layout = row.column()
            add_asset_layout.enabled = not add_possible

            add_asset = add_asset_layout.operator(operator="bevyassets.add", text="", icon="ADD")
            add_asset.target_type = target_type
            add_asset.target_name = target_name
            add_asset.asset_name = asset_registry.asset_name_selector
            add_asset.asset_type = asset_registry.asset_type_selector
            add_asset.asset_path = asset_registry.asset_path_selector

        panel.separator()

        for asset in user_assets:
            row = panel.row()
            row.prop(asset, "name", text="")
            #row.prop(asset, "path", text="")
            row.label(text=asset.path)
            asset_selector = row.operator(operator="asset.open_filebrowser", text="", icon="FILE_FOLDER")

            remove_asset = row.operator(operator="bevyassets.remove", text="", icon="TRASH")
            remove_asset.target_type = target_type
            remove_asset.target_name = target_name
            remove_asset.asset_path = asset.path
            """if not asset["internal"] and editable:
                remove_asset = row.operator(operator="bevyassets.remove", text="", icon="TRASH")
                remove_asset.target_type = target_type
                remove_asset.target_name = target_name
                remove_asset.asset_path = asset["path"]
            else:
                row.label(text="")"""
        for asset in generated_assets:
            pass

    return panel

class Blenvy_assets(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ""
    bl_parent_id = "BLENVY_PT_SidePanel"
    bl_options = {'DEFAULT_CLOSED','HIDE_HEADER'}
    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'ASSETS'
    
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

        name = "world"
        header, panel = layout.box().panel(f"assets{name}", default_closed=False)
        header.label(text="World/Level Assets")

        settings = {"blueprints_path": "blueprints", "export_gltf_extension": ".glb"}
        settings = SimpleNamespace(**settings)

        if panel:
            #print("dfs")
            for scene_selector in blenvy.main_scenes:
                scene = bpy.data.scenes[scene_selector.name]
                #get_main_scene_assets_tree(scene, blueprints_data, settings)
                user_assets = get_user_assets(scene)
                #print("user assets", user_assets, scene)
                row = panel.row()
                row.prop(scene, "always_export")

                scene_assets_panel = draw_assets(layout=row, name=scene.name, title=f"{scene.name} Assets", asset_registry=asset_registry, user_assets=user_assets, target_type="SCENE", target_name=scene.name)
                """if scene.name in blueprints_data.blueprint_instances_per_main_scene:
                    for blueprint_name in blueprints_data.blueprint_instances_per_main_scene[scene.name].keys():
                        blueprint = blueprints_data.blueprints_per_name[blueprint_name]
                        blueprint_assets = get_user_assets(blueprint.collection)
                        if scene_assets_panel:
                            row = scene_assets_panel.row()
                            draw_assets(layout=row, name=blueprint.name, title=f"{blueprint.name} Assets", asset_registry=asset_registry, assets=blueprint_assets, target_type="BLUEPRINT", target_name=blueprint.name)
"""