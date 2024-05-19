import bpy

from . import project_diff
from ...settings import are_settings_identical
from . import auto_export

# prepare export by gather the changes to the scenes & settings
def prepare_export():
    blenvy = bpy.context.window_manager.blenvy
    bpy.context.window_manager.auto_export_tracker.disable_change_detection()
    auto_export_settings = blenvy.auto_export
    if auto_export_settings.auto_export: # only do the actual exporting if auto export is actually enabled
        # determine changed objects
        previous_serialized_scene = None
        current_serialized_scene = None
        changes_per_scene = project_diff(previous_serialized_scene, current_serialized_scene)
        # determine changed parameters 
        previous_settings = None
        current_settings = None
        params_changed = are_settings_identical(previous_settings, current_settings)
        # do the actual export
        auto_export(changes_per_scene, params_changed, blenvy)

        # cleanup 
        # reset the list of changes in the tracker
        bpy.context.window_manager.auto_export_tracker.clear_changes()
        print("AUTO EXPORT DONE")            
        bpy.app.timers.register(bpy.context.window_manager.auto_export_tracker.enable_change_detection, first_interval=0.1)
