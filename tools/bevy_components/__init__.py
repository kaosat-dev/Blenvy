bl_info = {
    "name": "bevy_components",
    "author": "kaosigh",
    "version": (0, 4, 0),
    "blender": (3, 4, 0),
    "location": "VIEW_3D",
    "description": "UI to help create Bevy blueprints and components",
    "warning": "",
    "wiki_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow",
    "tracker_url": "https://github.com/kaosat-dev/Blender_bevy_components_workflow/issues/new",
    "category": "User Interface"
}

import bpy
from bpy.props import (StringProperty)

from .helpers import load_settings
from .blueprints import CreateBlueprintOperator
from .components.operators import CopyComponentOperator, RemoveComponentOperator, GenerateComponent_From_custom_property_Operator, PasteComponentOperator, AddComponentOperator, Toggle_ComponentVisibility

from .registry.registry import ComponentsRegistry,MissingBevyType
from .registry.operators import (COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL, COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT, COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_ALL, COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_CURRENT, ReloadRegistryOperator, OT_OpenFilebrowser)
from .registry.ui import (BEVY_COMPONENTS_PT_Configuration, BEVY_COMPONENTS_PT_MissingTypesPanel, MISSING_TYPES_UL_List)

from .components.metadata import (ComponentMetadata, ComponentsMeta, ensure_metadata_for_all_objects)
from .propGroups.prop_groups import (generate_propertyGroups_for_components)
from .components.lists import GENERIC_LIST_OT_actions, Generic_LIST_OT_AddItem, Generic_LIST_OT_RemoveItem, Generic_LIST_OT_SelectItem
from .components.definitions_list import (ComponentDefinitionsList, ClearComponentDefinitionsList)
from .components.ui import (BEVY_COMPONENTS_PT_ComponentsPanel)


# just a test, remove
def scan_item(item, nesting=0):
    try:
        for sub in dict(item).keys():
            print("--", sub, getattr(item[sub], "type_name", None), item[sub], nesting)
            try:
                scan_item(item[sub], nesting+1)
            except: 
                pass
    except:
        pass

class BEVY_COMPONENTS_PT_MainPanel(bpy.types.Panel):
    bl_idname = "BEVY_COMPONENTS_PT_MainPanel"
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"


    def draw_header(self, context):
        layout = self.layout
        name = context.object.name if context.object != None else ''
        layout.label(text="Components For "+ name)

    def draw(self, context):
        layout = self.layout
        object = context.object
        collection = context.collection

    
        """row.prop(bpy.context.window_manager, "blueprint_name")
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
        
        """



#_register, _unregister = bpy.utils.register_classes_factory(classes)
classes = [
    CreateBlueprintOperator,
    AddComponentOperator,  
    CopyComponentOperator,
    PasteComponentOperator,
    RemoveComponentOperator,
    GenerateComponent_From_custom_property_Operator,
    Toggle_ComponentVisibility,

    ComponentDefinitionsList,
    ClearComponentDefinitionsList,
    
    ComponentMetadata,
    ComponentsMeta,
    MissingBevyType,
    ComponentsRegistry,

    OT_OpenFilebrowser,
    ReloadRegistryOperator,
    COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_ALL,
    COMPONENTS_OT_REFRESH_CUSTOM_PROPERTIES_CURRENT,

    COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_ALL,
    COMPONENTS_OT_REFRESH_PROPGROUPS_FROM_CUSTOM_PROPERTIES_CURRENT,
    
    BEVY_COMPONENTS_PT_MainPanel,
    BEVY_COMPONENTS_PT_ComponentsPanel,
    BEVY_COMPONENTS_PT_Configuration,
    MISSING_TYPES_UL_List,
    BEVY_COMPONENTS_PT_MissingTypesPanel,

    Generic_LIST_OT_SelectItem,
    Generic_LIST_OT_AddItem,
    Generic_LIST_OT_RemoveItem,
    GENERIC_LIST_OT_actions
]

from bpy.app.handlers import persistent

@persistent
def post_load(file_name):
    registry = bpy.context.window_manager.components_registry
    if registry != None:
        registry.load_settings()
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.blueprint_name = StringProperty()
    bpy.app.handlers.load_post.append(post_load)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.WindowManager.blueprint_name
    
    bpy.app.handlers.load_post.remove(post_load)

