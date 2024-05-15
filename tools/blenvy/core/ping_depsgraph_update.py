import bpy
import rna_prop_ui

# fake way to make our operator's changes be visible to the change/depsgraph update handler in gltf_auto_export
def ping_depsgraph_update(object=None):
    if object == None:
        object = bpy.data.scenes[0]
    rna_prop_ui.rna_idprop_ui_create(object, "________temp", default=0)
    rna_prop_ui.rna_idprop_ui_prop_clear(object, "________temp")
    return None