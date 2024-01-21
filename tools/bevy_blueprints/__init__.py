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

from bpy_types import Operator, UIList
from bpy.props import (StringProperty, EnumProperty, PointerProperty, FloatVectorProperty)

from .blueprints import CreateBlueprintOperator
from .components.operators import CopyComponentOperator, DeleteComponentOperator, PasteComponentOperator, AddComponentOperator
from .components.registry import ComponentsRegistry
from .components.metadata import (ComponentInfos, ComponentsMeta, ensure_metadata_for_all_objects)
from .components.ui import (ComponentDefinitionsList, ClearComponentDefinitionsList, dynamic_properties_ui)


class MY_UL_List(UIList): 
    """Demo UIList.""" 
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE' # Make sure your code supports all 3 layout types 
        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            print("compact")
            #layout.label(text=item.name, icon = custom_icon) 
            layout.prop(item, "name", text="")

            #propertyGroup = getattr(object, item.component_name+"_ui")

        elif self.layout_type in {'GRID'}: 
            print("grid")
            layout.alignment = 'CENTER' 
            layout.label(text="", icon = custom_icon)

            


class Generic_LIST_OT_AddItem(Operator): 
    """Add a new item to the list.""" 
    bl_idname = "generic_list.add_item" 
    bl_label = "Add a new item" 


    property_group_name: StringProperty(
        name="property group name",
        description="",
    )

    def execute(self, context): 

        print("add to list", context.object, self.property_group_name)
        #context.scene.my_list.add() 
        my_list_container = getattr(context.object, self.property_group_name)
        my_list = getattr(my_list_container, "list")
        print("my list", my_list)
        item = my_list.add()
        item.name = ""
        item.component_name = "foo"
        print("added item", item.field_names)
        return{'FINISHED'}
    

class Generic_LIST_OT_RemoveItem(Operator): 
    """Remove an item to the list.""" 
    bl_idname = "generic_list.remove_item" 
    bl_label = "Remove a new item" 


    property_group_name: StringProperty(
        name="property group name",
        description="",
    )

    def execute(self, context): 
        print("remove from list", context.object, self.property_group_name)
       
        return{'FINISHED'}
    
    def execute(self, context): 
        print("remove from list", context.object, self.property_group_name)

        my_list_container = getattr(context.object, self.property_group_name)
        my_list = getattr(my_list_container, "list")
        index = getattr(my_list_container, "list_index")
        my_list.remove(index)
        my_list_container.list_index = min(max(0, index - 1), len(my_list) - 1) 
        return{'FINISHED'}


def draw_propertyGroup( propertyGroup, col):
    is_enum = getattr(propertyGroup, "with_enum")
    is_list = getattr(propertyGroup, "with_list") 
    # if it is an enum, the first field name is always the list of enum variants, the others are the variants
    field_names = propertyGroup.field_names

    if is_enum:
        subrow = col.row()
        display_name = field_names[0] if propertyGroup.tupple_or_struct == "struct" else ""
        subrow.prop(propertyGroup, field_names[0], text=display_name)
        subrow.separator()
        selection = getattr(propertyGroup, field_names[0])

        for fname in field_names[1:]:
            if fname == "variant_" + selection:
                subrow = col.row()
                display_name = fname if propertyGroup.tupple_or_struct == "struct" else ""

                nestedPropertyGroup = getattr(propertyGroup, fname)
                nested = getattr(nestedPropertyGroup, "nested", False)
                if not nested:
                    subrow.prop(propertyGroup, fname, text=display_name)
                    subrow.separator()
                else:
                    #print("deal with sub fields", nestedPropertyGroup.field_names)
                    for subfname in nestedPropertyGroup.field_names:
                        subrow = col.row()
                        display_name = subfname if nestedPropertyGroup.tupple_or_struct == "struct" else ""
                        subrow.prop(nestedPropertyGroup, subfname, text=display_name)
                        subrow.separator()
    elif is_list:
        #print("show list", propertyGroup, dict(propertyGroup))
        propertyGroup = getattr(bpy.context.object, "Vec<String>_ui") # FIXME: the prop group passed here is the wrong one
        item_list = getattr(propertyGroup, "list")
        list_item = getattr(propertyGroup, "item")
        print("list item", getattr(list_item, "field_names"), dict(list_item))
        print("item_list",propertyGroup , getattr(bpy.context.object, "Vec<String>_ui") )
        #for item in item_list:
        #    print("aaa", item.field_names)
        #    col.prop(item, "name")
        row = col.row()
        row.template_list("MY_UL_List", "The_List", propertyGroup, "list", propertyGroup, "list_index")
        
        row = col.column()
        op = row.operator('generic_list.add_item', text='+')
        op.property_group_name = "Vec<String>_ui"

        op = row.column().operator('generic_list.remove_item', text='REMOVE')
        op.property_group_name = "Vec<String>_ui"

        
    else: 
        for fname in field_names:
            subrow = col.row()

            nestedPropertyGroup = getattr(propertyGroup, fname)
            nested = getattr(nestedPropertyGroup, "nested", False)
            if nested:
                col.separator()
                col.label(text=fname) #  this is the name of the field/sub field
                col.separator()
                draw_propertyGroup(nestedPropertyGroup, col.row())
            else:
                display_name = fname if propertyGroup.tupple_or_struct == "struct" else ""
                subrow.prop(propertyGroup, fname, text=display_name)
                subrow.separator()


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

        # we get & load our component registry
        registry = bpy.context.window_manager.components_registry 
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

                component_meta =  next(filter(lambda component: component["name"] == component_name, components_in_object), None)
                if component_meta == None: 
                    continue

                # we fetch the matching ui property group
                propertyGroup = getattr(object, component_name+"_ui")
                row.prop(component_meta, "enabled", text="")
                row.label(text=component_name)
                col = row.column(align=True)
                print("component name", component_name)
                draw_propertyGroup(propertyGroup, col)

                #op = row.operator(CopyComponentOperator.bl_idname, text="", icon="SETTINGS")
                op = row.operator(DeleteComponentOperator.bl_idname, text="", icon="X")
                op.target_property = component_name
                
                op =row.operator(CopyComponentOperator.bl_idname, text="", icon="COPYDOWN")
                op.target_property = component_name
                op.source_object_name = object.name

            #print("TOOOO", registry.type_infos, registry.component_uis)
            """if registry.component_uis is not None:
                for component_name in sorted(registry.component_uis):

                    row = layout.row(align=True)
                    propertyGroup = getattr(object, component_name)
                    row.label(text=component_name)
                    col = row.column(align=True)
                    for fname in propertyGroup.field_names:
                        subrow = col.row()
                    
                        display_name = fname if propertyGroup.tupple_or_struct == "struct" else ""
                        subrow.prop(propertyGroup, fname, text=display_name)
                        subrow.separator()
                
                """
        else: 
            layout.label(text ="Select a collection/blueprint to edit it")

#_register, _unregister = bpy.utils.register_classes_factory(classes)
classes = [
    CreateBlueprintOperator,
    AddComponentOperator,  
    CopyComponentOperator,
    PasteComponentOperator,
    DeleteComponentOperator,

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
    bpy.context.window_manager.components_registry.load_schema()
    ensure_metadata_for_all_objects()
    dynamic_properties_ui()

@persistent
def init_data_if_needed(self):
    pass
    #ensure_metadata_for_all_objects()#very inneficient , find another way

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


    # just a test , remove later
    bpy.types.Object.foo = bpy.props.FloatVectorProperty(**{"description": "what the hell", "size":2})
    bpy.utils.register_class(MY_UL_List)

    bpy.utils.register_class(Generic_LIST_OT_AddItem)
    bpy.utils.register_class(Generic_LIST_OT_RemoveItem)

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

    del bpy.types.Object.foo