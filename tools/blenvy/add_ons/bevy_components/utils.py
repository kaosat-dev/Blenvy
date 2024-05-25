import bpy

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