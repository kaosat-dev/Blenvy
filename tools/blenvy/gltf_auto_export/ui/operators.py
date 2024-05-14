
import bpy
from bpy.types import Operator


class ASSETS_LIST_OT_actions(Operator):
    """Add / remove etc assets"""
    bl_idname = "asset_list.list_action"
    bl_label = "Asset Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}
    

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
            ('ADD', "Add", ""))) # type: ignore
    

    scene_type: bpy.props.StringProperty()#TODO: replace with enum

    def invoke(self, context, event):
        source = context.active_operator
        target_name = "library_scenes"
        target_index = "library_scenes_index"
        if self.scene_type == "level":
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
                setattr(source, target_index, current_index -1 )
                target.remove(idx)
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            new_scene_name = None
            if self.scene_type == "level":
                if context.window_manager.main_scene:
                    new_scene_name = context.window_manager.main_scene.name
            else:
                if context.window_manager.library_scene:
                    new_scene_name = context.window_manager.library_scene.name
            if new_scene_name:
                item = target.add()
                item.name = new_scene_name#f"Rule {idx +1}"

                if self.scene_type == "level":
                    context.window_manager.main_scene = None
                else:
                    context.window_manager.library_scene = None

                #name = f"Rule {idx +1}"
                #target.append({"name": name})
                setattr(source, target_index, len(target) - 1)
                #source[target_index] = len(target) - 1
                info = '"%s" added to list' % (item.name)
                self.report({'INFO'}, info)
        
        return {"FINISHED"}


import os
from bpy_extras.io_utils import ImportHelper

class OT_OpenFolderbrowser(Operator, ImportHelper):
    """Browse for registry json file"""
    bl_idname = "generic.open_folderbrowser" 
    bl_label = "Select folder" 

    # Define this to tell 'fileselect_add' that we want a directoy
    directory: bpy.props.StringProperty(
        name="Outdir Path",
        description="selected folder"
        # subtype='DIR_PATH' is not needed to specify the selection mode.
        # But this will be anyway a directory path.
        ) # type: ignore

    # Filters folders
    filter_folder: bpy.props.BoolProperty(
        default=True,
        options={"HIDDEN"}
        ) # type: ignore
    
    target_property: bpy.props.StringProperty(
        name="target_property",
        options={'HIDDEN'}
    ) # type: ignore
    
    def execute(self, context): 
        """Do something with the selected file(s)."""
        operator = context.active_operator
        new_path = self.directory
        target_path_name = self.target_property

        # path to the current blend file
        blend_file_path = bpy.data.filepath
        # Get the folder
        blend_file_folder_path = os.path.dirname(blend_file_path)
        print("blend_file_folder_path", blend_file_folder_path)
        print("new_path", self.directory, self.target_property, operator)

        path_names = ['export_assets_path', 'export_blueprints_path', 'export_levels_path', 'export_materials_path']
        export_root_path = operator.export_root_path
        export_assets_path = operator.export_assets_path
        #export_root_path_absolute = os.path.join(blend_file_folder_path, export_root_path)
        export_assets_path_full = os.path.join(blend_file_folder_path, export_root_path, export_assets_path)
        print("export_assets_path_full", export_assets_path_full)

        #new_root_path = os.path.join(blend_file_folder_path, new_path)
        if target_path_name == 'export_root_path':
            new_root_path_relative = os.path.relpath(new_path, blend_file_folder_path)
            print("changing root new_path to", self.directory, blend_file_folder_path, new_root_path_relative)
            # we need to change all other relative paths before setting the new absolute path
            for path_name in path_names:
                # get absolute path
                relative_path = getattr(operator, path_name, None)
                if relative_path is not None:
                    absolute_path = os.path.join(export_assets_path_full, relative_path)
                    print("absolute path for", path_name, absolute_path)
                    relative_path = os.path.relpath(absolute_path, new_path)
                    setattr(operator, path_name, relative_path)

            # store the root path as relative to the current blend file
            setattr(operator, target_path_name, new_path)

        else:
            relative_path = os.path.relpath(new_path, export_assets_path_full)
            setattr(operator, target_path_name, relative_path)

        #filename, extension = os.path.splitext(self.filepath) 
      
        
        return {'FINISHED'}
    
def draw_folder_browser(layout, label, value, target_property):
    row = layout.row()
    row.label(text=label)

    '''box = row.box()
    box.scale_y = 0.5
    box.label(text=value)'''

    col = row.column()
    col.enabled = False
    col.prop(bpy.context.active_operator, target_property, text="")

    folder_selector = row.operator(OT_OpenFolderbrowser.bl_idname, icon="FILE_FOLDER", text="")
    folder_selector.target_property = target_property #"export_root_path"