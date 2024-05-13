import bpy
import json


def draw_assets(layout, name, title, asset_registry, assets, target_type, target_name):
    header, panel = layout.box().panel(f"assets{name}", default_closed=False)
    header.label(text=title)
    if panel:
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
            if not asset["internal"]:
                remove_asset = row.operator(operator="bevyassets.remove", text="", icon="TRASH")
                remove_asset.target_type = target_type
                remove_asset.target_name = target_name
                remove_asset.asset_path = asset["path"]
            else:
                row.label(text="")

class GLTF_PT_auto_export_assets(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = ""
    bl_parent_id = "BLENVY_PT_SidePanel"
    bl_options = {'DEFAULT_CLOSED','HIDE_HEADER'}
    @classmethod
    def poll(cls, context):
        return context.window_manager.blenvy.mode == 'ASSETS'
    
    """def draw_header(self, context):
        layout = self.layout
        name = ""
        if context.collection is not None and context.collection.name == 'Scene Collection':
            name = f"WORLD/LEVEL: {context.scene.name}" 
        else:
            name = f"BLUEPRINT: {context.collection.name}"
        layout.label(text=f"Assets For {name}")"""

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        asset_registry = context.window_manager.assets_registry
        
        name = "world"
        header, panel = layout.box().panel(f"assets{name}", default_closed=False)
        header.label(text="World/Level Assets")

        if panel:
            for scene in bpy.data.scenes:
                if scene.name != "Library": # FIXME: hack for testing
                    assets = json.loads(scene.get('assets')) if 'assets' in scene else []
                    row = panel.row()
                    draw_assets(layout=row, name=scene.name, title=f"{scene.name} Assets", asset_registry=asset_registry, assets=assets, target_type="SCENE", target_name=scene.name)
