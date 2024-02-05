
import json
import bpy
from bpy_types import Operator
from bpy.props import (StringProperty)

from .helpers import make_empty

class CreateBlueprintOperator(Operator):
    """Creates blueprint"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    blueprint_name: StringProperty(
        name="blueprint name",
        description="blueprint name to add",
        default="NewBlueprint"
    )


    def execute(self, context):
        blueprint_name = self.blueprint_name
        if blueprint_name == '':
            blueprint_name = "NewBlueprint"
        collection = bpy.data.collections.new(blueprint_name)
        bpy.context.scene.collection.children.link(collection)
        collection['AutoExport'] = True

        # this is in order to deal with automatic naming
        blueprint_name = collection.name

        components_empty = make_empty(blueprint_name + "_components", [0,0,0], [0,0,0], [0,0,0], bpy.context.scene.collection)
        bpy.ops.collection.objects_remove_all()

        collection.objects.link(components_empty)

        components_empty.select_set(True)
        bpy.context.view_layer.objects.active = components_empty

        return {'FINISHED'}
    
