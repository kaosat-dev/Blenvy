import bpy

class GLTF_PT_auto_export_assets(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Assets"
    bl_parent_id = "GLTF_PT_auto_export_SidePanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        #if "auto_export_tracker" in context.window_manager:
        asset_registry = context.window_manager.assets_registry

        row = layout.row()
        row.prop(asset_registry, "asset_name_selector", text="")
        row.prop(asset_registry, "asset_type_selector", text="")
        row.prop(asset_registry, "asset_path_selector", text="")
        add_assets = row.operator(operator="bevyassets.add", text="Add asset")
        add_assets.asset_name = asset_registry.asset_name_selector
        add_assets.asset_type = asset_registry.asset_type_selector
        add_assets.asset_path = asset_registry.asset_path_selector

        layout.separator()
        row = layout.row()
        row.label(text="Name")
        row.label(text="Type")
        row.label(text="Path")
        row.label(text="Remove")

        for asset in asset_registry.assets_list:
            row = layout.row()
            row.label(text=asset["name"])
            row.label(text=asset["type"])
            row.label(text=asset["path"])
            if not asset["internal"]:
                remove_asset = row.operator(operator="bevyassets.remove", text="remove")
                remove_asset.asset_path = asset["path"]
            else:
                row.label(text="")