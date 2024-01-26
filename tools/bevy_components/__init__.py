bl_info = {
    "name": "bevy_components",
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

from bpy.props import (StringProperty)

from .blueprints import CreateBlueprintOperator
from .components.operators import CopyComponentOperator, DeleteComponentOperator, GenerateComponent_From_custom_property_Operator, PasteComponentOperator, AddComponentOperator, Toggle_ComponentVisibility

from .registry.registry import ComponentsRegistry,MissingBevyType
from .registry.operators import (ReloadRegistryOperator, OT_OpenFilebrowser)
from .registry.ui import (BEVY_COMPONENTS_PT_Configuration, BEVY_COMPONENTS_PT_MissingTypesPanel, MISSING_TYPES_UL_List)

from .components.metadata import (ComponentInfos, ComponentsMeta, do_object_custom_properties_have_missing_metadata, ensure_metadata_for_all_objects)
from .propGroups.prop_groups import (generate_propertyGroups_for_components)
from .components.lists import Generic_LIST_OT_AddItem, Generic_LIST_OT_RemoveItem, GENERIC_UL_List
from .components.definitions_list import (ComponentDefinitionsList, ClearComponentDefinitionsList)

def draw_propertyGroup( propertyGroup, col, nesting =[], rootName=None):
    is_enum = getattr(propertyGroup, "with_enum")
    is_list = getattr(propertyGroup, "with_list") 
    #current_short_name = getattr(propertyGroup, "short_name", "") + "_ui"
    #nesting = nesting + [current_short_name] # we need this convoluted "nested path strings " workaround so that operators working on a given
    # item in our components hierarchy can get the correct propertyGroup by STRINGS because of course, we cannot pass objects to operators...sigh

    # if it is an enum, the first field name is always the list of enum variants, the others are the variants
    field_names = propertyGroup.field_names
    # print("drawing", is_list, propertyGroup, nesting, "component_name", rootName)
    #type_name = getattr(propertyGroup, "type_name", None)#propertyGroup.type_name if "type_name" in propertyGroup else ""
    #print("type name", type_name)
    #print("name", propertyGroup.name, "name2", getattr(propertyGroup, "name"), "short_name", getattr(propertyGroup, "short_name", None), "nesting", nesting)
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
        #print("show list", propertyGroup, dict(propertyGroup), propertyGroup.type_name)
        item_list = getattr(propertyGroup, "list")
        item_type = getattr(propertyGroup, "type_name_short")
      
        for item in item_list:
            row = col.row().column()
            draw_propertyGroup(item, row, nesting, rootName)
        row = col.row()
    
        row = col.column()
        op = row.operator('generic_list.add_item', text='+')
        op.component_name = rootName
        op.property_group_path = json.dumps(nesting)

        op = row.column().operator('generic_list.remove_item', text='REMOVE')
        op.component_name = rootName
        op.property_group_path = json.dumps(nesting)

        
    else: 
        for fname in field_names:
            subrow = col.row()
            nestedPropertyGroup = getattr(propertyGroup, fname)
            nested = getattr(nestedPropertyGroup, "nested", False)
            display_name = fname if propertyGroup.tupple_or_struct == "struct" else ""

            if nested:
                col.separator()
                col.label(text=display_name) #  this is the name of the field/sub field
                col.separator()
                draw_propertyGroup(nestedPropertyGroup, col.row(), nesting + [fname], rootName )
            else:
                subrow.prop(propertyGroup, fname, text=display_name)
                subrow.separator()

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

class BEVY_COMPONENTS_PT_ComponentsPanel(bpy.types.Panel):
    bl_idname = "BEVY_COMPONENTS_PT_ComponentsPanel"
    bl_label = "Components"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"
    bl_parent_id = "BEVY_COMPONENTS_PT_MainPanel"

    def draw(self, context):
        object = context.object
        layout = self.layout

        # we get & load our component registry
        registry = bpy.context.window_manager.components_registry 
        available_components = bpy.context.window_manager.components_list


        if object is not None:
            row = layout.row(align=True)
            row.prop(available_components, "list", text="Component")
            row.prop(available_components, "filter",text="Filter")

            # add components
            row = layout.row(align=True)
            op = row.operator(AddComponentOperator.bl_idname, text="Add", icon="ADD")
            op.component_type = available_components.list
            row.enabled = available_components.list != ''

            layout.separator()

            # paste components
            row = layout.row(align=True)
            row.operator(PasteComponentOperator.bl_idname, text="Paste component ("+bpy.context.window_manager.copied_source_component_name+")", icon="PASTEDOWN")
            row.enabled = bpy.context.window_manager.copied_source_object != ''

            layout.separator()

            # upgrate custom props to components
            upgradeable_customProperties = registry.type_infos != None and do_object_custom_properties_have_missing_metadata(context.object)
            if upgradeable_customProperties:
                row = layout.row(align=True)
                op = row.operator(GenerateComponent_From_custom_property_Operator.bl_idname, text="generate components from custom properties" , icon="LOOP_FORWARDS") 
                layout.separator()


            components_in_object = object.components_meta.components
            for component_name in sorted(dict(object)) : # sorted by component name, practical
                if component_name == "components_meta": 
                    continue
                # anything withouth metadata gets skipped, we only want to see real components, not all custom props
                component_meta =  next(filter(lambda component: component["name"] == component_name, components_in_object), None)
                if component_meta == None: 
                    continue

                component_invalid = getattr(component_meta, "invalid")
                invalid_details = getattr(component_meta, "invalid_details")
                component_visible = getattr(component_meta, "visible")

                # our whole row 
                box = layout.box() 
                row = box.row(align=True)
                # "header"
                row.alert = component_invalid
                row.prop(component_meta, "enabled", text="")
                row.label(text=component_name)

                # we fetch the matching ui property group
                prop_group_location = row.column(align=False)#.split(factor=0.9)#layout.row(align=False)

                root_propertyGroup_name = component_name+"_ui"
                propertyGroup = getattr(component_meta, root_propertyGroup_name, None)
                if propertyGroup:
                    if component_visible:
                        if component_invalid:
                            error_message = invalid_details if component_invalid else "Missing component propertyGroup !"
                            prop_group_location.label(text=error_message)
                        draw_propertyGroup(propertyGroup, prop_group_location, [root_propertyGroup_name], component_name)
                    else :
                        row.label(text="details hidden, click on toggle to display")
                else:
                    error_message = invalid_details if component_invalid else "Missing component propertyGroup !"
                    row.label(text=error_message)

                # "footer" with additional controls
                op = row.operator(DeleteComponentOperator.bl_idname, text="", icon="X")
                op.component_name = component_name
                row.separator()
                
                op = row.operator(CopyComponentOperator.bl_idname, text="", icon="COPYDOWN")
                op.source_component_name = component_name
                op.source_object_name = object.name
                row.separator()
                
                toggle_icon = "TRIA_DOWN" if component_visible else "TRIA_RIGHT"
                op = row.operator(Toggle_ComponentVisibility.bl_idname, text="", icon=toggle_icon)
                op.component_name = component_name
                #row.separator()

        else: 
            layout.label(text ="Select a an object to edits its components")      

        """ col = layout.column(align=True)
        row = col.row(align=True)

        if object is not None:
            col = layout.column(align=True)
            row = col.row(align=True)

            row.prop(available_components, "list", text="Component")
            row.prop(available_components, "filter",text="Filter")

            # the button to add them
            row = col.row(align=True)
            op = row.operator(AddComponentOperator.bl_idname, text="Add", icon="ADD")
            row.enabled = available_components.list != ''

            op.component_type = available_components.list
            col.separator()
            col.separator()

         
          
            #print("object propgroups", dict(object))

            for component_name in sorted(dict(object)) : # sorted by component name, practical
                if component_name == "components_meta":
                    continue
                col = layout.column(align=True)
                row = col.row(align=True)

                

                
                #print("meta propgroups", dict(component_meta))

                row.prop(component_meta, "enabled", text="")
                row.label(text=component_name)

                col = row.column(align=True)

               
               

        else: 
            layout.label(text ="Select a collection/blueprint to edit it")"""


class BEVY_COMPONENTS_PT_MainPanel(bpy.types.Panel):
    bl_idname = "BEVY_COMPONENTS_PT_MainPanel"
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"


    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Components For "+ context.object.name)

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
    DeleteComponentOperator,
    GenerateComponent_From_custom_property_Operator,
    Toggle_ComponentVisibility,

    ComponentDefinitionsList,
    ClearComponentDefinitionsList,
    
    ComponentInfos,
    ComponentsMeta,
    MissingBevyType,
    ComponentsRegistry,

    OT_OpenFilebrowser,
    ReloadRegistryOperator,
    BEVY_COMPONENTS_PT_MainPanel,
    BEVY_COMPONENTS_PT_ComponentsPanel,
    BEVY_COMPONENTS_PT_Configuration,
    MISSING_TYPES_UL_List,
    BEVY_COMPONENTS_PT_MissingTypesPanel,

    GENERIC_UL_List,
    Generic_LIST_OT_AddItem,
    Generic_LIST_OT_RemoveItem
]

from bpy.app.handlers import persistent

@persistent
def post_load(file_name):
    print("post load", file_name)
    bpy.context.window_manager.components_registry.load_schema()
    generate_propertyGroups_for_components()
    ensure_metadata_for_all_objects()

@persistent
def init_data_if_needed(self):
    pass
    #ensure_metadata_for_all_objects()#very inneficient , find another way

def register():
    print("register")
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.blueprint_name = StringProperty()

    bpy.app.handlers.load_post.append(post_load)
    bpy.app.handlers.depsgraph_update_post.append(init_data_if_needed)


def unregister():
    print("unregister")
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.WindowManager.blueprint_name
    

    bpy.app.handlers.load_post.remove(post_load)
    bpy.app.handlers.depsgraph_update_post.remove(init_data_if_needed)

