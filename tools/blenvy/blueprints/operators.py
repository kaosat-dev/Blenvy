import os
import bpy
from bpy_types import (Operator)
from bpy.props import (StringProperty)

class OT_select_blueprint(Operator):
    """Select blueprint """
    bl_idname = "blueprint.select"
    bl_label = "Select blueprint"
    bl_options = {"UNDO"}

    blueprint_collection_name: StringProperty(
        name="blueprint collection name",
        description="blueprints to select's collection name ",
    ) # type: ignore

    blueprint_scene_name: StringProperty(
        name="blueprint scene name",
        description="blueprints to select's collection name ",
    ) # type: ignore

    def execute(self, context):
        if self.blueprint_collection_name:
            collection = bpy.data.collections[self.blueprint_collection_name]
            scene = bpy.data.scenes[self.blueprint_scene_name]
            if scene:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.window.scene = scene
                bpy.context.view_layer.objects.active = None
                bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[self.blueprint_collection_name]
                #bpy.context.view_layer.collections.active = collection
                #            bpy.context.view_layer.active_layer_collection = collection
                """for o in collection.objects:
                    o.select_set(True)"""

        return {'FINISHED'}
    