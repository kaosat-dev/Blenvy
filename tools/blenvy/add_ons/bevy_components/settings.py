import bpy
from bpy_types import (PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty)


# helper function to deal with timer
def toggle_watcher(self, context):
    #print("toggling watcher", self.watcher_enabled, watch_schema, self, bpy.app.timers)
    if not self.watcher_enabled:
        try:
            bpy.app.timers.unregister(watch_schema)
        except Exception as error:
            pass
    else:
        self.watcher_active = True
        bpy.app.timers.register(watch_schema)

def watch_schema():
    self = bpy.context.window_manager.components_registry
    # print("watching schema file for changes")
    try:
        stamp = os.stat(self.schemaFullPath).st_mtime
        stamp = str(stamp)
        if stamp != self.schemaTimeStamp and self.schemaTimeStamp != "":
            print("FILE CHANGED !!", stamp,  self.schemaTimeStamp)
            # see here for better ways : https://stackoverflow.com/questions/11114492/check-if-a-file-is-not-open-nor-being-used-by-another-process
            """try:
                os.rename(path, path)
                #return False
            except OSError:    # file is in use
                print("in use")
                #return True"""
            #bpy.ops.object.reload_registry()
            # we need to add an additional delay as the file might not have loaded yet
            bpy.app.timers.register(lambda: bpy.ops.object.reload_registry(), first_interval=1)

        self.schemaTimeStamp = stamp
    except Exception as error:
        pass
    return self.watcher_poll_frequency if self.watcher_enabled else None


class ComponentsSettings(PropertyGroup):
    schemaPath: StringProperty(
        name="schema path",
        description="path to the registry schema file",
        default="registry.json"
    )# type: ignore

    watcher_enabled: BoolProperty(name="Watcher_enabled", default=True, update=toggle_watcher)# type: ignore
    watcher_active: BoolProperty(name = "Flag for watcher status", default = False)# type: ignore

    watcher_poll_frequency: IntProperty(
        name="watcher poll frequency",
        description="frequency (s) at wich to poll for changes to the registry file",
        min=1,
        max=10,
        default=1
    )# type: ignore
    
    schemaTimeStamp: StringProperty(
        name="last timestamp of schema file",
        description="",
        default=""
    )# type: ignore
