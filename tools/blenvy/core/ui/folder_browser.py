
import bpy
import os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator    

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
        operator = context.window_manager.blenvy
        new_path = self.directory
        target_path_name = self.target_property

        # path to the current blend file
        blend_file_path = bpy.data.filepath
        # Get the folder
        blend_file_folder_path = os.path.dirname(blend_file_path)
        print("blend_file_folder_path", blend_file_folder_path)
        print("new_path", self.directory, self.target_property, operator)

        asset_path_names = ['export_assets_path', 'export_blueprints_path', 'export_levels_path', 'export_materials_path']
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
            for path_name in asset_path_names:
                # get current relative path
                relative_path = getattr(operator, path_name, None)
                if relative_path is not None:
                    # and now get absolute path of asset_path 
                    absolute_path = os.path.join(export_assets_path_full, relative_path)
                    print("absolute path for", path_name, absolute_path)
                    relative_path = os.path.relpath(absolute_path, new_path)
                    setattr(operator, path_name, relative_path)

            # store the root path as relative to the current blend file
            setattr(operator, target_path_name, new_path)
        elif target_path_name == 'export_assets_path':
            pass
        else:
            relative_path = os.path.relpath(new_path, export_assets_path_full)
            setattr(operator, target_path_name, relative_path)

        #filename, extension = os.path.splitext(self.filepath) 
      
        
        return {'FINISHED'}