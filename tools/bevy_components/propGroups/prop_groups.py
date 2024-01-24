import bpy

from .conversions import property_group_value_to_custom_property_value
from .process_component import process_component
from .utils import update_calback_helper

## main callback function, fired whenever any property changes, no matter the nesting level
def update_component(self, context, definition, component_name):
    registry = bpy.context.window_manager.components_registry
    current_object = bpy.context.object
    update_disabled = current_object["__disable__update"] if "__disable__update" in current_object else False
    if update_disabled:
        return
    
    #component_name = definition["short_name"]
    print("update in component", self, component_name)#, type_def, type_info,self,self.name , "context",context.object.name, "attribute name", field_name)
    components_in_object = current_object.components_meta.components
    component_meta =  next(filter(lambda component: component["name"] == component_name, components_in_object), None)
    self = getattr(component_meta, component_name+"_ui") #getattr(current_object, component_name+"_ui") # FIXME: yikes, I REALLY dislike this ! using the context out of left field
    # we use our helper to set the values
    context.object[component_name] = property_group_value_to_custom_property_value(self, definition, registry)


def generate_propertyGroups_for_components():
    registry = bpy.context.window_manager.components_registry
    if registry.type_infos == None:
        registry.load_type_infos()

    type_infos = registry.type_infos

    for component_name in type_infos:
        definition = type_infos[component_name]
        short_name = definition["short_name"]
        is_component = definition['isComponent'] if "isComponent" in definition else False
        root_property_name = short_name if is_component else None

        foo = update_calback_helper(definition, update_component, root_property_name)
        print("ROOT LEVEL", root_property_name)
        process_component(registry, definition, foo, None, root_property_name,  []) # (lambda short: short)(definition["short_name"]))
