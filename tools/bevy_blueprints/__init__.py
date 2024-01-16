bl_info = {
    "name": "bevy_blueprints",
    "author": "kaosigh",
    "version": (0, 0, 1),
    "blender": (3, 4, 0),
    "location": "VIEW_3D",
    "description": "UI to help create Bevy blueprints and components",
    "warning": "",
    "wiki_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow",
    "tracker_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow/issues/new",
    "category": "User Interface"
}
import os
import bpy
import json

from bpy_types import Operator
from bpy.props import (StringProperty, EnumProperty, PointerProperty, FloatVectorProperty)

from .blueprints import CreateBlueprintOperator
from .components.operators import CopyComponentOperator, DeleteComponentOperator, PasteComponentOperator, AddComponentOperator
from .components.definitions import (ComponentDefinition)
from .components.registry import ComponentsRegistry, read_components
from .components.metadata import (ComponentInfos, ComponentsMeta, ensure_metadata_for_all_objects)
from .components.ui import (ComponentDefinitionsList, ClearComponentDefinitionsList, dynamic_properties_ui, generate_enum_properties, unregister_stuff)

class BEVY_BLUEPRINTS_PT_TestPanel(bpy.types.Panel):
    bl_idname = "BEVY_BLUEPRINTS_PT_TestPanel"
    bl_label = "Bevy Components"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"


    def draw(self, context):
        layout = self.layout
        object = context.object
        collection = context.collection
        registry_raw = bpy.context.window_manager.components_registry.raw_registry
        registry_raw = json.loads(registry_raw)

        # we get & load our component registry
        registry = bpy.context.window_manager.components_registry.registry 
        registry = json.loads(registry) if registry != '' else ''
        available_components = bpy.context.window_manager.components_list

        col = layout.column(align=True)
        row = col.row(align=True)
        
        row.prop(bpy.context.window_manager, "blueprint_name")
        op = row.operator(CreateBlueprintOperator.bl_idname, text="Create blueprint", icon="CONSOLE")
        op.blueprint_name = bpy.context.window_manager.blueprint_name
        layout.separator()

        current_components_container = None
        has_components = False
        for child in collection.objects:
            if child.name.endswith("_components"):
                has_components = True
                current_components_container= child



        if collection is not None and has_components:
            layout.label(text="Edit blueprint: "+ collection.name)
        if object is not None:
            
            col = layout.column(align=True)
            row = col.row(align=True)

            #row.operator(ClearComponentDefinitionsList.bl_idname, text="clear")
            row.prop(available_components, "list", text="Component")
            row.prop(available_components, "filter",text="Filter")

            # the button to add them
            op = row.operator(AddComponentOperator.bl_idname, text="Add", icon="CONSOLE")
            op.component_type = available_components.list
            col.separator()

            # past components
            row = col.row(align=True)
            row.operator(PasteComponentOperator.bl_idname, text="Paste component ("+bpy.context.window_manager.copied_source_component_name+")", icon="PASTEDOWN")
            row.enabled = bpy.context.window_manager.copied_source_object != ''

            col.separator()

            components_in_object = object.components_meta.components

            for component_name in sorted(dict(object)) : # sorted by component name, practical
                if component_name == "components_meta":
                    continue
                col = layout.column(align=True)
                row = col.row(align=True)

                component_value = object[component_name]
                component_meta =  next(filter(lambda component: component["name"] == component_name, components_in_object), None)
                if component_meta == None: 
                    continue
                component_type = component_meta.type_name
                component_enabled = component_meta.enabled

                # for testing, remove later
                foo_data = json.loads(component_meta.data)
                component_type = foo_data["type_info"]


                #print("component_meta", component_meta)
                #component_data = json.loads(component_meta.data)
                #print("component_type", component_type)
                # row.enabled = component_enabled
                #row.prop(object.reusable_enum, "list")

                row.prop(component_meta, "enabled", text="")
                row.label(text=component_name)

                if component_type == "string": 
                    row.prop(object, '["'+ component_name +'"]', text="")#, placeholder="placeholder")
                elif component_type == "Enum":
                    #custom_enum = getattr(object, groupName)
                    enum_name = "enum_"+component_name
                    propertyGroup = getattr(object, enum_name)
                    row.prop(propertyGroup, "enum", text="")

                    # row.prop(object, enum_name, text="")
                elif component_type == "object":
                    row.label(text="------------")
                else :
                    row.prop(object, '["'+ component_name +'"]', text="")
                    
                #op = row.operator(CopyComponentOperator.bl_idname, text="", icon="SETTINGS")
                op = row.operator(DeleteComponentOperator.bl_idname, text="", icon="X")
                op.target_property = component_name
                
                op =row.operator(CopyComponentOperator.bl_idname, text="", icon="COPYDOWN")
                op.target_property = component_name
                op.source_object_name = object.name

            for truc in bpy.testcomponents:
                #print("truc", truc)
                row = col.row(align=True)
                ui_thingy_name = truc
                propertyGroup = getattr(object, ui_thingy_name)
                #print("propgroup", propertyGroup, dict(propertyGroup), propertyGroup.single_item)
                row.label(text=truc)
                for fname in propertyGroup.field_names:
                    display_name = fname if propertyGroup.tupple_or_struct == "struct" else ""
                    row.prop(propertyGroup, fname, text=display_name)
                #registry_raw
                #
        else: 
            layout.label(text ="Select a collection/blueprint to edit it")



#_register, _unregister = bpy.utils.register_classes_factory(classes)

classes = [
    CreateBlueprintOperator,
    AddComponentOperator,  
    CopyComponentOperator,
    PasteComponentOperator,
    DeleteComponentOperator,

    ComponentDefinition,
    ComponentDefinitionsList,
    ClearComponentDefinitionsList,
    
    ComponentInfos,
    ComponentsMeta,
    ComponentsRegistry,

    BEVY_BLUEPRINTS_PT_TestPanel,
]

from bpy.app.handlers import persistent

@persistent
def post_load(file_name):
    print("post load", file_name)
    read_components()
    generate_enum_properties()
    ensure_metadata_for_all_objects()

    dynamic_properties_ui()

@persistent
def init_data_if_needed(self):
    ensure_metadata_for_all_objects()

def register():
    print("register")

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.blueprint_name = StringProperty()
    bpy.types.Object.components_meta = PointerProperty(type=ComponentsMeta)
    bpy.types.WindowManager.components_registry = PointerProperty(type=ComponentsRegistry)

    bpy.types.WindowManager.copied_source_component_name = StringProperty()
    bpy.types.WindowManager.copied_source_object = StringProperty()

    bpy.app.handlers.load_post.append(post_load)
    bpy.app.handlers.depsgraph_update_post.append(init_data_if_needed)


def unregister():
    print("unregister")
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.blueprint_name
    del bpy.types.Object.components_meta
    del bpy.types.WindowManager.components_registry

    del bpy.types.WindowManager.copied_source_component_name
    del bpy.types.WindowManager.copied_source_object

    bpy.app.handlers.load_post.remove(post_load)
    bpy.app.handlers.depsgraph_update_post.remove(init_data_if_needed)

    #unregister_stuff()