
import json
import bpy
from bpy_types import Operator

from .components.registry import read_components
from .helpers import make_empty3

class CreateBlueprintOperator(Operator):
    """Print object name in Console"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    def execute(self, context):
        print("calling operator")
        print (context.object)

        blueprint_name = "NewBlueprint"
        collection = bpy.data.collections.new(blueprint_name)
        bpy.context.scene.collection.children.link(collection)

        collection['AutoExport'] = True

        blueprint_name = collection.name

        components_empty = make_empty3(blueprint_name + "_components", [0,0,0], [0,0,0], [0,0,0])
        bpy.ops.collection.objects_remove_all()

        collection.objects.link(components_empty)


        #bpy.context.window_manager.components_registry.registry.clear()
        bpy.context.window_manager.components_registry.registry = json.dumps(read_components())
        


        return {'FINISHED'}
    
