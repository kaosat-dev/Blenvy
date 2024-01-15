import ast
import json
import bpy
from bpy_types import Operator
from bpy.props import (StringProperty, EnumProperty, PointerProperty, FloatVectorProperty)

from .metadata import cleanup_invalid_metadata

class AddComponentOperator(Operator):
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
        object = context.object
        component_definitions = context.window_manager.component_definitions

        has_component_type = self.component_type != ""
        #existing_component = has_component_type and component_infos.name in object
        cleanup_invalid_metadata(object)
        if object is not None and has_component_type:
            component_infos = component_definitions[int(self.component_type)]
            long_name = component_infos.long_name
            short_name = component_infos.name
         
            data = json.loads(component_infos.data)

            print("component infos", data, "long_name", component_infos.long_name)
            type_name = data["type"]
            default_value = data["value"]

            def make_bool():
                object[component_infos.name] = default_value

            def make_string():
                object[component_infos.name] = default_value

            def make_color():
                object[component_infos.name] = default_value
                property_manager = object.id_properties_ui(component_infos.name)
                property_manager.update(subtype='COLOR')

            def make_enum():
                object[component_infos.name] = component_infos.values

            component_prop_makers = {
                "Bool": make_bool,
                "Color": make_color,
                "String":make_string,
                "Enum":make_enum
            }

            if type_name in component_prop_makers:
                component_prop_makers[type_name]()
            else :
                object[component_infos.name] = default_value

            data["enabled"] = True


            registry = bpy.context.window_manager.components_registry.registry 
            registry = json.loads(registry)
            registry_entry = registry[long_name] if long_name in registry else None
            print("registry_entry", registry_entry)


            #object.components_meta.components.clear()
            components_in_object = object.components_meta.components
            for bla in components_in_object:
                print("components in object", bla.name)

            matching_component = next(filter(lambda component: component["name"] == short_name, components_in_object), None)
            print("matching", matching_component)
            # matching component means we already have this type of component 
            if matching_component:
                return {'FINISHED'}
            
           

            component_meta = components_in_object.add()
            component_meta.name = short_name
            component_meta.long_name = long_name
            component_meta.data = component_infos.data
            component_meta.type_name = data["type"]

            """
            object[component_infos.name] = 0.5
            property_manager = object.id_properties_ui(component_infos.name)
            property_manager.update(min=-10, max=10, soft_min=-5, soft_max=5)

            print("property_manager", property_manager)

            object[component_infos.name] = [0.8,0.2,1.0]
            property_manager = object.id_properties_ui(component_infos.name)
            property_manager.update(subtype='COLOR')"""

            #IDPropertyUIManager
            #rna_ui = object[component_infos.name].get('_RNA_UI')
            #print("RNA", rna_ui)

            
            #object[component_infos.name] = FloatVectorProperty(name="Hex Value", 
            #                            subtype='COLOR', 
            #                            default=[0.0,0.0,0.0])
            #lookup[component_infos.type_name] if component_infos.type_name in lookup else  ""


            #my_enum = object.titi.add()

        return {'FINISHED'}

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
        object = context.object      
        if object is not None: 
            del object[self.target_property]

        return {'FINISHED'}

class PasteComponentOperator(Operator):
    """Paste component to blueprint"""
    bl_idname = "object.paste_component"
    bl_label = "Paste component to blueprint Operator"

    def execute(self, context):
        print("pasting component to blueprint")
        print (context.object)
        

        return {'FINISHED'}
    


