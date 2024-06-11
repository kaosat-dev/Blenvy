import bpy
from .constants import HIDDEN_COMPONENTS

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
        return 'Object'
    if isinstance(selection, bpy.types.Collection):
        return 'Collection'

def add_component_to_ui_list(self, context, _):
        print("add components to ui_list")
        items = []
        type_infos = context.window_manager.components_registry.type_infos
        for long_name in type_infos.keys():
            definition = type_infos[long_name]
            short_name = definition["short_name"]
            is_component = definition['isComponent']  if "isComponent" in definition else False
            """if self.filter.lower() in short_name.lower() and is_component:"""
            if not 'Handle' in short_name and not "Cow" in short_name and not "AssetId" in short_name and short_name not in HIDDEN_COMPONENTS: # FIXME: hard coded, seems wrong
                items.append((long_name, short_name))
        items.sort(key=lambda a: a[1])
        return items


def is_component_valid_and_enabled(object, component_name):
    if "components_meta" in object or hasattr(object, "components_meta"):
        target_components_metadata = object.components_meta.components
        component_meta = next(filter(lambda component: component["long_name"] == component_name, target_components_metadata), None)
        if component_meta != None:
            return component_meta.enabled and not component_meta.invalid
    return True