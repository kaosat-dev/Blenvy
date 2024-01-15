import bpy
import json
import os
from pathlib import Path

from bpy_types import (PropertyGroup)

# this is where we store the information for all available components
class ComponentsRegistry(PropertyGroup):
    registry: bpy.props. StringProperty(
        name="registry",
        description="component registry"
    )

    
def read_components():
    file_path = bpy.data.filepath
    # Get the folder
    folder_path = os.path.dirname(file_path)
    path =  os.path.join(folder_path, "../schema.json")
    print("path to defs", path)
    f = Path(bpy.path.abspath(path)) # make a path object of abs path
    mapped = {}

    if f.exists():
        print("COMPONENT DEFINITIONS")
        bpy.context.window_manager.component_definitions.clear()

        with open(path) as f: 
            data = json.load(f) 
            defs = data["$defs"]
            # print ("DEFS", defs) 
            for name in defs:
                definition = data["$defs"][name]
                is_component = definition['isComponent']  if "isComponent" in definition else False
                is_resource = definition['is_resource']  if "is_resource" in definition else False

                # base types
                #if not is_component and not is_resource:
                component_data = add_component_to_mapped(mapped=mapped, name=name, definitions=defs)

                
                if is_component and name.startswith("bevy_bevy_blender_editor_basic_example::"):
                    print("definition:", name, definition, definition['isComponent'])
                    item = bpy.context.window_manager.component_definitions.add()
                    item.name = component_data["name"]
                    item.long_name = name
                    item.type_name = component_data["type"]
                    item.data = json.dumps(component_data)
    return mapped


def add_component_to_mapped(mapped, name, definitions):
    if name in mapped:
        #print("already present")
        return mapped[name]
    print("computing", name)
    short_name = str(name)
    long_name = str(name)
    if "::" in name:
        short_name = short_name.rsplit('::', 1)[-1]

    if not name in definitions:
        mapped[name] = {
            "name": short_name,
            "long_name": long_name,
            "type_info": None,
            "type": None,
            "value": None,
            "values": []
        }
        return mapped[name]
    definition = definitions[name]
    is_component = definition['isComponent']  if "isComponent" in definition else False
    is_resource = definition['is_resource']  if "is_resource" in definition else False

    type_info = definition["typeInfo"] if "typeInfo" in definition else None
    type = definition["type"] if "type" in definition else None
    properties = definition["properties"] if "properties" in definition else {}
    prefixItems = definition["prefixItems"] if "prefixItems" in definition else []
    values = definition["enum"] if "enum" in definition else []
    default_value = ''
    sub_type = None



    #special overrides, not a fan, but we have special parsing of glam type in bevy_gltf_components anyway
    overrides_map = {
        "glam::Vec2": "Vec2",
        "glam::Vec3": "Vec3",
        "glam::Vec4": "Vec3",
        "bevy_render::color::Color": "Color"
    }
    type = overrides_map[name] if name in overrides_map else type

  
    # TODO: add overrides for various vec2s & vec3s
    base_type_map = {
        "string":" ",
        "boolean": True,
        "float": 0.0,
        "uint": 0,
        "int":0,

        "Vec2": [0.0, 0.0],
        "Vec3": [0.0, 0.0, 0.0],
        "Vec4": [0.0, 0.0, 0.0, 0.0], 
        "Color": [1.0, 1.0, 0.0, 1.0]
    }
    default_value = base_type_map[type] if type in base_type_map else ""
    if type_info == "Enum" and not name in overrides_map.keys():
        default_value = values[0] if len(values) > 0 else ''

    if len(properties.keys()) > 0 and not name in overrides_map.keys():
        default_value = {}
        for property_name in properties.keys():
            ref_name = properties[property_name]["type"]["$ref"].replace("#/$defs/", "")
            #print("ref_name", ref_name, "property_name", property_name)
            if ref_name in mapped:
                original = mapped[ref_name]
                default_value[property_name] = original["value"]
                #print("ORIGINAL PROP", original)
            else: 
                #print("need to compute", ref_name)
                original = add_component_to_mapped(mapped=mapped, name=ref_name, definitions=definitions)
                #print("original", original)
                default_value[property_name] = original["value"]
                

    if len(prefixItems) > 0 and not name in overrides_map.keys():
        default_value = []
        prefix_infos = []
        for index, item in enumerate(prefixItems):
            ref_name = item["type"]["$ref"].replace("#/$defs/", "")
            if ref_name in mapped:
                original = mapped[ref_name]
                default_value.append(original["value"])
                prefix_infos.append(original)
                print("ORIGINAL prefix item", original)
            else:
                #print("need to compute", ref_name)
                original = add_component_to_mapped(mapped=mapped, name=ref_name, definitions=definitions)
                print("original", original)
                default_value.append(original["value"])
                prefix_infos.append(original)
        print("DEFAULT", default_value)
        if len(default_value) == 1:
            default_value = default_value[0]#default_value = [0.0, 0.0, 0.0]
            infos = prefix_infos[0]
            type = infos["type"]
            if infos["type_info"] == "Enum" and type != "Color":
                type = 'Enum'
           
            print("single value, using only that one", infos, default_value)



    remapped_data = {
        "name": short_name,
        "long_name": long_name,
        "type_info": type_info,
        "type": type,
        "sub_type": sub_type,
        "value": default_value,
        "values": values
    }   

    print("adding", name)
    mapped[name] = remapped_data
    return remapped_data


