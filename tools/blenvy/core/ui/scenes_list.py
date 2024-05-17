import bpy
from bpy.types import Operator

class SCENE_UL_Blenvy(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    #   flt_flag is the result of the filtering process for this item.
    #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
    #         need them.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            #if ma:
            #    layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
            #else:
            #    layout.label(text="", translate=False, icon_value=icon)
            layout.label(text=item.name, icon_value=icon)
            #layout.prop(item, "name", text="", emboss=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class SCENES_LIST_OT_actions(Operator):
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
            ('ADD', "Add", ""))
    ) # type: ignore

    scene_type: bpy.props.EnumProperty(
        items=(
            ('LEVEL', "Level", ""),
            ('LIBRARY', "Library", ""),
        )
    ) # type: ignore
    
    def invoke(self, context, event):
        source = context.window_manager.blenvy
        target_name = "library_scenes"
        target_index = "library_scenes_index"
        if self.scene_type == "LEVEL":
            target_name = "main_scenes"
            target_index = "main_scenes_index"
        
        target = getattr(source, target_name)
        idx = getattr(source, target_index)
        current_index = getattr(source, target_index)

        try:
            item = target[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(target) - 1:
                target.move(idx, idx + 1)
                setattr(source, target_index, current_index +1 )
                info = 'Item "%s" moved to position %d' % (item.name, current_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                target.move(idx, idx - 1)
                setattr(source, target_index, current_index -1 )
                info = 'Item "%s" moved to position %d' % (item.name, current_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (target[idx].name)
                target.remove(idx)

                setattr(source, target_index, current_index -1 )
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            new_scene_name = None
            if self.scene_type == "LEVEL":
                if context.window_manager.main_scene:
                    new_scene_name = context.window_manager.main_scene.name
            else:
                if context.window_manager.library_scene:
                    new_scene_name = context.window_manager.library_scene.name
            if new_scene_name:
                item = target.add()
                item.name = new_scene_name

                if self.scene_type == "LEVEL":
                    context.window_manager.main_scene = None
                else:
                    context.window_manager.library_scene = None

                setattr(source, target_index, len(target) - 1)

                

                info = '"%s" added to list' % (item.name)
                self.report({'INFO'}, info)
        
        return {"FINISHED"}
