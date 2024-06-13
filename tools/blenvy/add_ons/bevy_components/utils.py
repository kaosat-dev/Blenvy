import bpy
from .constants import HIDDEN_COMPONENTS
from bpy.props import StringProperty, EnumProperty
from bpy_types import Operator
from blenvy.core.helpers_collections import (set_active_collection)

def get_collection_scene(collection):
    for scene in bpy.data.scenes:
        if scene.user_of_id(collection):
            return scene
    return None

class BLENVY_OT_item_select(Operator):
    """Select object by name"""
    bl_idname = "blenvy.select_item"
    bl_label = "Select item (object or collection)"
    bl_options = {"UNDO"}

    item_type : EnumProperty(
        name="item type",
        description="type of the item to select: object or collection",
        items=(
            ('OBJECT', "Object", ""),
            ('COLLECTION', "Collection", ""),
            ),
        default="OBJECT"
    ) # type: ignore

    target_name: StringProperty(
        name="target name",
        description="target to select's name ",
    ) # type: ignore

    def execute(self, context):
        if self.target_name:
            if self.item_type == "OBJECT":
                object = bpy.data.objects[self.target_name]
                scenes_of_object = list(object.users_scene)
                if len(scenes_of_object) > 0:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.window.scene = scenes_of_object[0]
                    object.select_set(True)    
                    bpy.context.view_layer.objects.active = object
            elif self.item_type == "COLLECTION":
                collection = bpy.data.collections[self.target_name]
                scene_of_collection = get_collection_scene(collection)
                if scene_of_collection is not None:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.window.scene = scene_of_collection
                    bpy.context.view_layer.objects.active = None
                    set_active_collection(bpy.context.window.scene, collection.name)


        return {'FINISHED'}

#FIXME: does not work if object is hidden !!
def get_selected_object_or_collection(context):
    target = None
    object = next(iter(context.selected_objects), None)
    collection = context.collection
    if object is not None:
        target = object
    elif collection is not None:
        target = collection
    return target


def get_selection_type(selection):
    if isinstance(selection, bpy.types.Object):
        return 'OBJECT'
    if isinstance(selection, bpy.types.Collection):
        return 'COLLECTION'

def get_item_by_type(item_type, item_name):
    item = None
    if item_type == 'OBJECT':
        item = bpy.data.objects[item_name]
    elif item_type == 'COLLECTION':
        print("item NAME", item_name)
        item = bpy.data.collections[item_name]
    return item

def get_selected_object_or_collection_by_item_type(context, item_type):
    item = None
    if item_type == 'OBJECT':
        object = next(iter(context.selected_objects), None)
        return object
    elif item_type == 'COLLECTION':
        return context.collection

def add_component_to_ui_list(self, context, _):
        items = []
        type_infos = context.window_manager.components_registry.type_infos
        for long_name in type_infos.keys():
            definition = type_infos[long_name]
            short_name = definition["short_name"]
            is_component = definition['isComponent']  if "isComponent" in definition else False
            """if self.filter.lower() in short_name.lower() and is_component:"""
            if is_component and not 'Handle' in short_name and not "Cow" in short_name and not "AssetId" in short_name and short_name not in HIDDEN_COMPONENTS: # FIXME: hard coded, seems wrong
                items.append((long_name, short_name))
        items.sort(key=lambda a: a[1])
        return items


def is_component_valid_and_enabled(object, component_name):
    if "components_meta" in object or hasattr(object, "components_meta"):
        target_components_metadata = object.components_meta.components
        component_meta = next(filter(lambda component: component["long_name"] == component_name, target_components_metadata), None)
        if component_meta is not None:
            return component_meta.enabled and not component_meta.invalid
    return True