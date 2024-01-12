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
from .helpers import make_empty3
from .components import (ComponentDefinition, ComponentDefinitions, AddComponentDefinitions, ClearComponentDefinitions)
from pathlib import Path

stored_component = None
bla = PointerProperty()

class CreateBlueprintOperator(Operator):
    """Print object name in Console"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    def execute(self, context):
        print("calling operator")
        print (context.object)

        blueprint_name = "NewBlueprint"
        collection = bpy.data.collections.new(blueprint_name)
        bpy.context.scene.collection.children.link(collection)

        collection['AutoExport'] = True

        blueprint_name = collection.name

        components_empty = make_empty3(blueprint_name + "_components", [0,0,0], [0,0,0], [0,0,0])
        bpy.ops.collection.objects_remove_all()

        collection.objects.link(components_empty)

        init_components()


        return {'FINISHED'}
    
class AddComponentToBlueprintOperator(Operator):
    """Add component to blueprint"""
    bl_idname = "object.addblueprint_to_component"
    bl_label = "Add component to blueprint Operator"

    component_type: StringProperty(
        name="component_type",
        description="component type to add",
    )

    def execute(self, context):
        print("adding component to blueprint", self.component_type)
        original_active_object = bpy.context.active_object

        # fixme: refactor, do this better
        collection = context.collection
        current_components_container = None
        for child in collection.objects:
            if child.name == collection.name + "_components":
                current_components_container= child

        if current_components_container is not None and self.component_type != "":
            value = ""
            # Struct + empty properties => Struct with no fields => str (for now)
            component_infos = bpy.context.collection.component_definitions[int(self.component_type)]
            data = json.loads(component_infos.toto)

            print("component infos", component_infos, component_infos.type_name)
            type_name = component_infos.type_name
            default_value = data["value"]

  
            def make_bool():
                current_components_container[component_infos.name] = default_value

            def make_string():
                current_components_container[component_infos.name] = default_value

            def make_color():
                current_components_container[component_infos.name] = default_value
                property_manager = current_components_container.id_properties_ui(component_infos.name)
                property_manager.update(subtype='COLOR')

            def make_enum():
                current_components_container[component_infos.name] = component_infos.values

            component_prop_makers = {
                "Bool": make_bool,
                "Color": make_color,
                "String":make_string,
                "Enum":make_enum
            }

            if type_name in component_prop_makers:
                component_prop_makers[type_name]()
            else :
                current_components_container[component_infos.name] = default_value
            """
            current_components_container[component_infos.name] = 0.5
            property_manager = current_components_container.id_properties_ui(component_infos.name)
            property_manager.update(min=-10, max=10, soft_min=-5, soft_max=5)

            print("property_manager", property_manager)

            current_components_container[component_infos.name] = [0.8,0.2,1.0]
            property_manager = current_components_container.id_properties_ui(component_infos.name)
            property_manager.update(subtype='COLOR')"""

            #IDPropertyUIManager
            #rna_ui = current_components_container[component_infos.name].get('_RNA_UI')
            #print("RNA", rna_ui)

            
            #current_components_container[component_infos.name] = FloatVectorProperty(name="Hex Value", 
            #                            subtype='COLOR', 
            #                            default=[0.0,0.0,0.0])
            #lookup[component_infos.type_name] if component_infos.type_name in lookup else  ""


        return {'FINISHED'}

import ast

class CopyComponentOperator(Operator):
    """Copy component from blueprint"""
    bl_idname = "object.copy_component"
    bl_label = "Copy component from blueprint Operator"


    target_property: StringProperty(
        name="component_name",
        description="component to copy",
    )

    target_property_value: StringProperty(
        name="component_value",
        description="component value to copy",
    )

    def execute(self, context):
        print("copying component to blueprint")
        print ("infos", self.target_property, self.target_property_value)
        print("recast", ast.literal_eval(self.target_property_value))

        #stored_component

        return {'FINISHED'}
    
class DeleteComponentOperator(Operator):
    """Delete component from blueprint"""
    bl_idname = "object.delete_component"
    bl_label = "Delete component from blueprint Operator"
    bl_options = {"REGISTER", "UNDO"}

    target_property: StringProperty(
        name="component_name",
        description="component to delete",
    )

    def execute(self, context):
        print("delete component to blueprint")
        print (context.object)

        # fixme: refactor, do this better
        collection = context.collection
        current_components_container = None
        for child in collection.objects:
            if child.name == collection.name + "_components":
                current_components_container= child
        if current_components_container is not None: 
            del current_components_container[self.target_property]

        return {'FINISHED'}

class PasteComponentOperator(Operator):
    """Paste component to blueprint"""
    bl_idname = "object.paste_component"
    bl_label = "Paste component to blueprint Operator"

    def execute(self, context):
        print("pasting component to blueprint")
        print (context.object)
        

        return {'FINISHED'}

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

        #row.prop(obj, "show_name", toggle=True, icon="FILE_FONT", text="Create blueprint")

        col.operator(CreateBlueprintOperator.bl_idname, text="Create blueprint", icon="CONSOLE")
        layout.separator()

        #layout.label(text =obj.name)
        # layout.label(text =context.collection.name)
        # and hasattr(collection, 'AutoExport')
        current_components_container = None
        has_components = False
        for child in collection.objects:
            if child.name.endswith("_components"):
                has_components = True
                current_components_container= child

        # layout.label(text= "has_components" + str(has_components))
        if collection is not None and has_components:
            layout.label(text="Edit blueprint: "+ collection.name)
            col = layout.column(align=True)
            row = col.row(align=True)

            # display list of available components
            #row.prop(collection,"my_enum",text="Component")

            row.operator(ClearComponentDefinitions.bl_idname, text="clear")

            row.prop(collection.components, "list", text="Component")

            # the button to add them
            op = row.operator(AddComponentToBlueprintOperator.bl_idname, text="Add", icon="CONSOLE")
            op.component_type = collection.components.list
            """print("collection.components.list", collection.components.list)

            foo = list(
                map(lambda x: print("name:", x.name, ", type:", x.type_name, ", values: ", x.values), collection.component_definitions.values())
            )"""
            #print("component_definitions", foo)

            

            layout.operator(PasteComponentOperator.bl_idname, text="Paste component", icon="PASTEDOWN")

            #layout.prop(component_types, "")
            # components_empty_name = collection.name + "_components"
            # fixme: hack for toggling components
            # current_components_container["enableds"] = {}
            #current_components_container["toto"] = False
            
         
            for component_name in dict(current_components_container):
                #bla["enabled"] = False
                col = layout.column(align=True)
                row = col.row(align=True)

                component_value = current_components_container[component_name]
               
                
                # row.prop(current_components_container, '["'+ component_name +'"].name', text="")
                row.label(text=component_name)

                # add a "disabled" pseudo property for all of the components
                #row.prop(current_components_container.enableds, "enabled", text="")
                if current_components_container[component_name] != '' :
                    row.prop(current_components_container, '["'+ component_name +'"]', text="")
                else :
                    row.label(text="------------")
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


classes = [
    CreateBlueprintOperator,
    AddComponentToBlueprintOperator,  
    CopyComponentOperator,
    PasteComponentOperator,
    DeleteComponentOperator,

    ComponentDefinition,
    ComponentDefinitions,
    AddComponentDefinitions, 
    ClearComponentDefinitions,
    BEVY_BLUEPRINTS_PT_TestPanel,
]

def getList(scene, context):
    print("context, definitions:", len(context.collection.component_definitions))
    for i in context.collection.component_definitions:
        print("aa", i)
    items = []
    """if context.object.type == "MESH":
        items += [("1","Mesh Item 1","This is a mesh list."),
                  ("2","Mesh Item 2","This is a mesh list.")]
    else:"""
    items.append(("Collider","Collider","This is a non-mesh list."))
    items.append(("Rigidbody","Rigidbody","This is a non-mesh list."))
    items.append(("Dynamic","Dynamic","This is a non-mesh list."))
    items.append(("Pickable","Pickable","This is a non-mesh list."))
    items.append(("Healer","Healer","This is a non-mesh list."))

    return items


#_register, _unregister = bpy.utils.register_classes_factory(classes)

def init_components():
    file_path = bpy.data.filepath
    # Get the folder
    folder_path = os.path.dirname(file_path)
    path =  os.path.join(folder_path, "../schema.json")
    print("path to defs", path)
    f = Path(bpy.path.abspath(path)) # make a path object of abs path

    if f.exists():
        print("COMPONENT DEFINITIONS")

        with open(path) as f: 
            data = json.load(f) 
            defs = data["$defs"]
            # print ("DEFS", defs) 
            for name in defs:
                definition = data["$defs"][name]
                if definition['isComponent'] and name.startswith("bevy_bevy_blender_editor_basic_example::"):
                    #print("definition:", name, definition, definition['isComponent'])

                    type_info = definition["typeInfo"] if "typeInfo" in definition else None
                    properties = definition["properties"] if "properties" in definition else {}
                    prefixItems = definition["prefixItems"] if "prefixItems" in definition else []
                    default_value = ''
                    values = definition["enum"] if "enum" in definition else [None]

                    short_name = name
                    if "::" in name:
                        short_name = name.rsplit('::', 1)[-1]


                    print("definition", name, "type_info", type_info, "values", values)

                    type = type_info
                    if type_info == "Struct" and len(properties.keys()) > 0:
                        type = "Struct"
                    if type_info == "TupleStruct" and len(prefixItems) == 1:
                        if prefixItems[0]["type"]["$ref"] == "#/$defs/bool":
                            type = "Bool"
                            default_value = True

                        elif prefixItems[0]["type"]["$ref"] == "#/$defs/bevy_render::color::Color":
                            type = "Color"
                            default_value = [0.8,0.2,1.0]

                        elif prefixItems[0]["type"]["$ref"] == "#/$defs/alloc::string::String":
                            type = "String"
                            default_value = ' '

                        elif prefixItems[0]["type"]["$ref"] == "#/$defs/f32":
                            type = "Float"
                            default_value = 0.0

                        elif prefixItems[0]["type"]["$ref"] == "#/$defs/u64":
                            type = "UInt"
                            default_value = 0

                        elif prefixItems[0]["type"]["$ref"] == "#/$defs/glam::Vec2":
                            type = "Vec2"
                            default_value = [0.0, 0.0]
                        elif prefixItems[0]["type"]["$ref"] == "#/$defs/glam::Vec3":
                            type = "Vec3"
                            default_value = [0.0, 0.0, 0.0]
                            
                    if type_info == "TupleStruct" and len(prefixItems) > 1:
                        for item in prefixItems:
                            ref = item["type"]["$ref"].replace("#/$defs/", "")
                            original = data["$defs"][ref]
                            print("ORIGINAL", original)
                        
                    if type_info == "Enum":
                        type = "Enum"

                    if type_info is not None:
                        item = bpy.context.collection.component_definitions.add()
                        item.name = short_name
                        item.long_name = name
                        item.type_name = type
                        item.value = str(default_value)
                        item.values = str(values[0])

                        new_item = {
                                "name": short_name,
                                "long_name": name,
                                "type_name": type,
                                "value": default_value,
                                "values": values
                        }
                        item.toto = json.dumps(new_item)
                        print("new _item", new_item)


                        

                
        #print(f.read_text())

def register():
    print("register")
    bpy.types.Collection.my_enum = bpy.props.EnumProperty(name="myEnum",description="a dynamic list",items=getList)

    for cls in classes:
        bpy.utils.register_class(cls)

    #bpy.app.handlers.load_post.append(init_components)
    #bpy.app.handlers.version_update

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
