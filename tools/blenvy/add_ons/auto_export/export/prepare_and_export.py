import bpy

from .project_diff import get_changes_per_scene, project_diff, serialize_current
from .auto_export import auto_export
from .settings_diff import get_setting_changes

# prepare export by gather the changes to the scenes & settings
def prepare_and_export():
    print("prepare and export")
    bpy.context.window_manager.auto_export_tracker.disable_change_detection()
    blenvy = bpy.context.window_manager.blenvy
    auto_export_settings = blenvy.auto_export
    if auto_export_settings.auto_export: # only do the actual exporting if auto export is actually enabled

        # determine changed objects
        per_scene_changes = get_changes_per_scene()
        # determine changed parameters 
        setting_changes = get_setting_changes()
        # do the actual export
        auto_export(per_scene_changes, setting_changes, blenvy)

        # cleanup 
        # TODO: these are likely obsolete
        # reset the list of changes in the tracker
        bpy.context.window_manager.auto_export_tracker.clear_changes()
        print("AUTO EXPORT DONE")            
        bpy.app.timers.register(bpy.context.window_manager.auto_export_tracker.enable_change_detection, first_interval=0.1)
