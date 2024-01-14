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
from .components.operators import CopyComponentOperator, DeleteComponentOperator, PasteComponentOperator, AddComponentToBlueprintOperator
from .components.helpers import (ComponentDefinition, ComponentDefinitions, ClearComponentDefinitions, ComponentEnums, ComponentMeta, FooBar, Foos)
from .components.registry import ComponentsRegistry

stored_component = None
bla = PointerProperty()
current_toto = None

    




class BEVY_BLUEPRINTS_PT_TestPanel(bpy.types.Panel):
    bl_idname = "BEVY_BLUEPRINTS_PT_TestPanel"
    bl_label = "Bevy Components"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bevy Components"
    bl_context = "objectmode"


    def draw(self, context):
        layout = self.layout
        obj = context.object
        collection = context.collection

        layout.label(text="Create blueprint:")

        col = layout.column(align=True)
        row = col.row(align=True)

        col.operator(CreateBlueprintOperator.bl_idname, text="Create blueprint", icon="CONSOLE")
        layout.separator()

        current_components_container = None
        has_components = False
        for child in collection.objects:
            if child.name.endswith("_components"):
                has_components = True
                current_components_container= child

        if collection is not None and has_components:
            layout.label(text="Edit blueprint: "+ collection.name)
            col = layout.column(align=True)
            row = col.row(align=True)

            row.operator(ClearComponentDefinitions.bl_idname, text="clear")
            row.prop(collection.components, "list", text="Component")

            # the button to add them
            op = row.operator(AddComponentToBlueprintOperator.bl_idname, text="Add", icon="CONSOLE")
            op.component_type = collection.components.list
            """print("collection.components.list", collection.components.list)

            foo = list(
                map(lambda x: print("name:", x.name, ", type:", x.type_name, ", values: ", x.values), collection.component_definitions.values())
            )"""

            layout.operator(PasteComponentOperator.bl_idname, text="Paste component", icon="PASTEDOWN")
            
            # we get & load our component registry
            registry = bpy.context.window_manager.components_registry.registry 
            registry = json.loads(registry)
            components_in_object = current_components_container.components_meta.components


            for component_name in dict(current_components_container):
                if component_name == "components_meta":
                    continue
                col = layout.column(align=True)
                row = col.row(align=True)

                component_value = current_components_container[component_name]
                component_meta =  next(filter(lambda component: component["name"] == component_name, components_in_object), None)
                if component_meta == None: 
                    continue
                component_type = component_meta.type_name

                #print("component_meta", component_meta)
                #component_data = json.loads(component_meta.data)
                print("component_type", component_type)
                
                row.prop(component_meta, "enabled", text="")
                row.label(text=component_name)

                if component_type == "string": 
                    row.prop(current_components_container, '["'+ component_name +'"]', text="")#, placeholder="placeholder")
                elif component_type == "Enum":
                    pass
                    #component_enums = collection.component_enums
                    #row.prop(current_components_container, "toto", text="")
                elif component_type == "object":
                    row.label(text="------------")
                else :
                    row.prop(current_components_container, '["'+ component_name +'"]', text="")
                    


                op = row.operator(CopyComponentOperator.bl_idname, text="", icon="SETTINGS")
               

                op = row.operator(DeleteComponentOperator.bl_idname, text="", icon="X")
                op.target_property = component_name
                
                op =row.operator(CopyComponentOperator.bl_idname, text="", icon="COPYDOWN")
                op.target_property = component_name
                op.target_property_value = str(component_value)
                #layout.prop(obj,'["boolean"]',text='test')

                # bpy.ops.wm.properties_remove
                #bpy.ops.wm.properties_add()

        else: 
            layout.label(text ="Select a collection/blueprint to edit it")



#_register, _unregister = bpy.utils.register_classes_factory(classes)

classes = [
    CreateBlueprintOperator,
    AddComponentToBlueprintOperator,  
    CopyComponentOperator,
    PasteComponentOperator,
    DeleteComponentOperator,

    ComponentDefinition,
    ComponentDefinitions,
    ClearComponentDefinitions,
    
    ComponentEnums,
    ComponentMeta,
    ComponentsRegistry,

    BEVY_BLUEPRINTS_PT_TestPanel,

]


def register():
    print("register")

    for cls in classes:
        bpy.utils.register_class(cls)


    bpy.types.Object.components_meta = PointerProperty(type=ComponentMeta)
    bpy.types.Collection.component_enums = PointerProperty(type=ComponentEnums)
    bpy.types.WindowManager.components_registry = PointerProperty(type=ComponentsRegistry)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Collection.component_enums
    del bpy.types.Object.components_meta
    del bpy.types.WindowManager.components_registry

    #del bpy.types.Object.toto

    #del bpy.types.Collection.my_enum
    
