
import bpy
from bpy.types import Operator

class CUSTOM_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "scene_list.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))
    

    scene_type: bpy.props.StringProperty()#TODO: replace with enum

    def invoke(self, context, event):
        print("INVOKE", self.scene_type, "gltf_auto_export")
        source = bpy.context.preferences.addons["gltf_auto_export"].preferences
        target_name = "library_scenes"
        target_index = "library_scenes_index"
        if self.scene_type == "level":
            target_name = "main_scenes"
            target_index = "main_scenes_index"
        
        target = getattr(source, target_name)
        idx = getattr(source, target_index)

        try:
            item = target[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(target) - 1:
                item_next = target[idx + 1].name
                target.move(idx, idx + 1)
                source[target_index] += 1
                info = 'Item "%s" moved to position %d' % (item.name, source[target_index] + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = target[idx - 1].name
                target.move(idx, idx - 1)
                source[target_index] -= 1
                info = 'Item "%s" moved to position %d' % (item.name, source[target_index] + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (target[idx].name)
                source[target_index] -= 1
                target.remove(idx)
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            new_scene_name = None
            if self.scene_type == "level":
                if context.scene.main_scene:
                    new_scene_name = context.scene.main_scene.name
            else:
                if context.scene.library_scene:
                    new_scene_name = context.scene.library_scene.name
            if new_scene_name:
                item = target.add()
                item.name = new_scene_name#f"Rule {idx +1}"

                if self.scene_type == "level":
                    context.scene.main_scene = None
                else:
                    context.scene.library_scene = None

                #name = f"Rule {idx +1}"
                #target.append({"name": name})

                source[target_index] = len(target) - 1
                info = '"%s" added to list' % (item.name)
                self.report({'INFO'}, info)
        
        return {"FINISHED"}


