from types import SimpleNamespace
import bpy
from .assets_scan import get_main_scene_assets_tree
from .asset_helpers import get_assets


def draw_assets(layout, name, title, asset_registry, assets, target_type, target_name, editable=True):
    header, panel = layout.box().panel(f"assets{name}", default_closed=False)
    header.label(text=title)
    if panel:
        if editable:
            row = panel.row()
            row.prop(asset_registry, "asset_name_selector", text="")
            row.prop(asset_registry, "asset_type_selector", text="")
            asset_selector = row.operator(operator="asset.open_filebrowser", text="", icon="FILE_FOLDER")
            
            if asset_registry.asset_type_selector == 'IMAGE':
                asset_selector.filter_glob = '*.jpg;*.jpeg;*.png;*.bmp'
            if asset_registry.asset_type_selector == 'MODEL':
                asset_selector.filter_glob="*.glb;*.gltf"
            if asset_registry.asset_type_selector == 'TEXT':
                asset_selector.filter_glob="*.txt;*.md;*.ron;*.json"
            if asset_registry.asset_type_selector == 'AUDIO':
                asset_selector.filter_glob="*.mp3;*.wav;*.flac"

            add_asset = row.operator(operator="bevyassets.add", text="", icon="ADD")
            add_asset.target_type = target_type
            add_asset.target_name = target_name
            add_asset.asset_name = asset_registry.asset_name_selector
            add_asset.asset_type = asset_registry.asset_type_selector
            add_asset.asset_path = asset_registry.asset_path_selector

        #assets = json.loads(blueprint.collection["assets"]) if "assets" in blueprint.collection else []
        for asset in assets:
            row = panel.row()
            row.label(text=asset["name"])
            row.label(text=asset["type"])
            row.label(text=asset["path"])
            if not asset["internal"] and editable:
                remove_asset = row.operator(operator="bevyassets.remove", text="", icon="TRASH")
                remove_asset.target_type = target_type
                remove_asset.target_name = target_name
                remove_asset.asset_path = asset["path"]
            else:
                row.label(text="")

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

        layout.operator(operator="bevyassets.test")

        asset_registry = context.window_manager.assets_registry
        blueprints_registry = context.window_manager.blueprints_registry
        blueprints_registry.add_blueprints_data()
        blueprints_data = blueprints_registry.blueprints_data

        name = "world"
        header, panel = layout.box().panel(f"assets{name}", default_closed=False)
        header.label(text="World/Level Assets")

        settings = {"export_blueprints_path": "blueprints", "export_gltf_extension": ".glb"}
        settings = SimpleNamespace(**settings)

        if panel:
            for scene in bpy.data.scenes:
                if scene.name != "Library": # FIXME: hack for testing
                    get_main_scene_assets_tree(scene, blueprints_data, settings)

                    direct_assets = get_assets(scene)
                    row = panel.row()
                    scene_assets_panel = draw_assets(layout=row, name=scene.name, title=f"{scene.name} Assets", asset_registry=asset_registry, assets=direct_assets, target_type="SCENE", target_name=scene.name)
                    if scene.name in blueprints_data.blueprint_instances_per_main_scene:
                        for blueprint_name in blueprints_data.blueprint_instances_per_main_scene[scene.name].keys():
                            blueprint = blueprints_data.blueprints_per_name[blueprint_name]
                            blueprint_assets = get_assets(blueprint.collection)
                            if scene_assets_panel:
                                row = scene_assets_panel.row()
                                draw_assets(layout=row, name=blueprint.name, title=f"{blueprint.name} Assets", asset_registry=asset_registry, assets=blueprint_assets, target_type="BLUEPRINT", target_name=blueprint.name)
