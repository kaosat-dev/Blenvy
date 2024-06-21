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
            ('MESH', "Mesh", ""),
            ('MATERIAL', "Material", ""),
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

def get_selected_item(context):
    selection = None

    #print("original context", context)
    def get_outliner_area():
        if bpy.context.area.type!='OUTLINER':
            for area in bpy.context.screen.areas:
                if area.type == 'OUTLINER':
                    return area
        return None

    area = get_outliner_area()
    if area is not None:
        region = next(region for region in area.regions if region.type == "WINDOW")

        with bpy.context.temp_override(area=area, region=region):
            #print("overriden context", bpy.context)
            for obj in bpy.context.selected_ids:
                pass#print(f"Selected: {obj.name} - {type(obj)}")
            selection = bpy.context.selected_ids[len(bpy.context.selected_ids) - 1] if len(bpy.context.selected_ids)>0 else None #next(iter(bpy.context.selected_ids), None)
            print("selection", f"Selected: {selection.name} - {type(selection)}")

    #print("SELECTIONS", context.selected_objects)
    return selection


def get_selection_type(selection):
    #print("bla mesh", isinstance(selection, bpy.types.Mesh), "bli bli", selection.type)
    if isinstance(selection, bpy.types.Material):
        return 'MATERIAL'
    if isinstance(selection, bpy.types.Mesh):
        return 'MESH'
    if isinstance(selection, bpy.types.Object):
        return 'OBJECT'
    if isinstance(selection, bpy.types.Collection):
        return 'COLLECTION'

def get_item_by_type(item_type, item_name):
    item = None
    if item_type == 'OBJECT':
        item = bpy.data.objects[item_name]
    elif item_type == 'COLLECTION':
        item = bpy.data.collections[item_name]
    elif item_type == "MESH":
        item = bpy.data.meshes[item_name]
    elif item_type == 'MATERIAL':
        item = bpy.data.materials[item_name]
    return item

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