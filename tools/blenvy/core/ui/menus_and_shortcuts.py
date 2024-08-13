import bpy
import json
from mathutils import Vector

from ..helpers_collections import set_active_collection
from ..blenvy_manager import BlenvyManager

""" This file contains quality of life operators/menus/shortcuts to make working with blueprints more pleasant
* based on the excellent work by slyedoc: https://github.com/slyedoc/bevy_sly_blender/tree/4223cc0ff86255f82bb555ffc8eddf65e91aa636

- [ ] detect editing in progress
- [x] select collection instead of objects 
- [ ] if current scene (before edit) 
    - is library: do not create instance
    - is main scene: create instance
- or alternative: sub menu to choose instance creation or not
- [x] save & restore blenvy mode
- [x] add a contextual shortcut to easilly jump in/out of editing mode
- [ ] save & reset camera
"""

def edit_or_create_blueprint_menu(self, context):
    if bpy.context.active_object and bpy.context.active_object.instance_collection:
        self.layout.operator(BLENVY_OT_ui_blueprint_edit_start.bl_idname)
    else:
        blenvy = context.window_manager.blenvy # type: BlenvyManager                
        prev_scene = bpy.data.scenes.get(blenvy.edit_blueprint_previous_scene)
        if prev_scene is not None:
            self.layout.operator(BLENVY_OT_ui_blueprint_edit_end.bl_idname)
        else:
            self.layout.operator(BLENVY_OT_ui_blueprint_create.bl_idname)
        

class BLENVY_OT_ui_blueprint_create_or_edit(bpy.types.Operator):
    """Create Blueprint in a new Scene"""
    bl_idname = "window_manager.blenvy_blueprint_shortcut"
    bl_label = "Edit Blueprint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):        
        blenvy = context.window_manager.blenvy # type: BlenvyManager    
        if bpy.context.active_object and bpy.context.active_object.instance_collection:
            bpy.ops.window_manager.blenvy_edit_blueprinrt()
        else:
            blenvy = context.window_manager.blenvy # type: BlenvyManager                
            prev_scene = bpy.data.scenes.get(blenvy.edit_blueprint_previous_scene)
            if prev_scene is not None:
                bpy.ops.window_manager.blenvy_exit_edit_blueprint()
            else:
                bpy.ops.window_manager.blenvy_create_blueprint()
        
        return {"FINISHED"}

class BLENVY_OT_ui_blueprint_create(bpy.types.Operator):
    """Create Blueprint in a new Scene"""
    bl_idname = "window_manager.blenvy_create_blueprint"
    bl_label = "Create Blueprint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):        
        blenvy = context.window_manager.blenvy # type: BlenvyManager        

        # Store original Blenvy setting
        blenvy.edit_blueprint_previous_scene = bpy.context.scene.name
        blenvy.edit_blueprint_previous_mode = blenvy.mode

        # set mode to components
        blenvy.mode = "COMPONENTS"

        blueprint_name = "new_blueprint"
        collection = bpy.data.collections.new(blueprint_name)
        
        library_scene_name = "Library"
        if len(blenvy.library_scenes_names) > 0:
            library_scene_name = blenvy.library_scenes_names[0]
        else:
            bpy.data.scenes.new(library_scene_name)
        # automatically add it to the library : find library scene, if any, if not, create it 
        bpy.data.scenes[library_scene_name].collection.children.link(collection)
        

        # create an instance of the 
        source_collection = collection
        instance_obj = bpy.data.objects.new(
            name=collection.name, 
            object_data=None
        )
        instance_obj.instance_collection = source_collection
        instance_obj.instance_type = 'COLLECTION'
        parent_collection = bpy.context.view_layer.active_layer_collection
        parent_collection.collection.objects.link(instance_obj)

        # now open the temporary scene
        scene_name = f"temp:{blueprint_name}"
        bpy.ops.scene.new(type="EMPTY")
        new_scene = bpy.context.scene
        new_scene.name = scene_name
        bpy.context.window.scene = new_scene

   
        new_scene.collection.children.link(collection)

        # deselect all objects then select the first object in new scene
        bpy.ops.object.select_all(action='DESELECT')        

        # zoom to selected
        bpy.ops.view3d.view_selected()
        # now that the 3d view has been adapted, we select what we actually need: the collection/blueprint
        bpy.ops.blenvy.select_item(target_name=collection.name, item_type="COLLECTION", override_scene_name=scene_name)

        return {"FINISHED"}

class BLENVY_OT_ui_blueprint_edit_start(bpy.types.Operator):
    """Edit the Blueprint referenced by this Blueprint Instance in a new Scene"""
    bl_idname = "window_manager.blenvy_edit_blueprinrt"
    bl_label = "Start Editing Blueprint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):        
        blenvy = context.window_manager.blenvy # type: BlenvyManager        
        collection = bpy.context.active_object.instance_collection

        # Store original Blenvy setting
        blenvy.edit_blueprint_previous_scene = bpy.context.scene.name
        blenvy.edit_blueprint_previous_mode = blenvy.mode

        # set mode to components
        blenvy.mode = "COMPONENTS"

        if not collection:
            print("Active item is not a Blueprint/Collection instance")
            self.report({"WARNING"}, "Active item is not a Blueprint/Collection instance")
            return {"CANCELLED"}

        scene_name = f"temp:{collection.name}"
        bpy.ops.scene.new(type="EMPTY")
        new_scene = bpy.context.scene
        new_scene.name = scene_name
        bpy.context.window.scene = new_scene
        new_scene.collection.children.link(collection)

        # Assuming you want to focus on the objects from the linked collection
        # Switch to the new scene context        
        
        """blenvy.edit_collection_world_texture = "checker"
        if blenvy.edit_collection_world_texture != "none":
            world = bpy.data.worlds.new(bpy.context.scene.name)
            new_scene.world = world
            world.use_nodes = True
            tree = world.node_tree

            if blenvy.edit_collection_world_texture in ["checker", "checker_view"]:
                checker_texture = tree.nodes.new("ShaderNodeTexChecker")
                checker_texture.inputs["Scale"].default_value = 20
                checker_texture.location = Vector((-250, 0))
                if blenvy.edit_collection_world_texture == "checker_view":
                    coord = tree.nodes.new("ShaderNodeTexCoord")
                    coord.location = Vector((-500, 0))
                    for op in coord.outputs:
                        op.hide = True
                    tree.links.new(coord.outputs["Window"], checker_texture.inputs["Vector"])
                tree.links.new(checker_texture.outputs["Color"], tree.nodes["Background"].inputs["Color"])
            elif blenvy.edit_collection_world_texture == "gray":
                tree.nodes["Background"].inputs["Color"].default_value = (.3, .3, .3, 1)"""

        # deselect all objects then select the first object in new scene
        bpy.ops.object.select_all(action='DESELECT')        

        # find the root object
        if len(collection.objects) > 0 :
            root_obj = collection.objects[0]
            while root_obj.parent:
                root_obj = root_obj.parent            
            
            # select object and children
            new_scene.objects[root_obj.name].select_set(True)        
            # def select_children(parent):
            #     for child in parent.children:
            #         child.select_set(True)
            #         select_children(child)  # Recursively select further descendants
            # select_children(root_obj);

            # Select the view layer and view the selected objects
            bpy.context.view_layer.objects.active = new_scene.objects[root_obj.name]
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]

            # zoom to selected
            bpy.ops.view3d.view_selected()
        
        # now that the 3d view has been adapted, we select what we actually need: the collection/blueprint        
        bpy.ops.blenvy.select_item(target_name=collection.name, item_type="COLLECTION", override_scene_name=scene_name)

        return {"FINISHED"}
    
class BLENVY_OT_ui_blueprint_edit_end(bpy.types.Operator):    
    bl_idname = "window_manager.blenvy_exit_edit_blueprint"
    bl_label = "Done editing blueprint"
    bl_options = {"UNDO"}
    
    def execute(self, context):
        blenvy = context.window_manager.blenvy # type: BlenvyManager        
        # = context.window_manager.bevy # type: BlenvyManager
        
        current_scene = bpy.context.scene      
        prev_scene = bpy.data.scenes.get(blenvy.edit_blueprint_previous_scene)

        # we are done editing the blueprint, reset settings to the way they were before
        blenvy.edit_blueprint_previous_scene = ""
        blenvy.mode = blenvy.edit_blueprint_previous_mode


        if prev_scene is None:
            print("No scene to return to")
            return {'CANCELLED'}
        
        if current_scene.name.startswith("temp:"):
            bpy.data.scenes.remove(bpy.context.scene)
            bpy.context.window.scene = prev_scene
        else:
            #if 
            print("Not in temp scene")
            return {'CANCELLED'}

        return {'FINISHED'}

