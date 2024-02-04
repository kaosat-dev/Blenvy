import bpy

def detect_context_mismatch():
    return bpy.context.scene == bpy.context.window.scene