
import os
import json
import bpy
from pathlib import Path

from ..core.scene_helpers import add_scene_property

def find_blueprints_not_on_disk(blueprints, folder_path, extension):
    not_found_blueprints = []
    for blueprint in blueprints:
        gltf_output_path = os.path.join(folder_path, blueprint.name + extension)
        # print("gltf_output_path", gltf_output_path)
        found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
        if not found:
            not_found_blueprints.append(blueprint)
    return not_found_blueprints

def check_if_blueprint_on_disk(scene_name, folder_path, extension):
    gltf_output_path = os.path.join(folder_path, scene_name + extension)
    found = os.path.exists(gltf_output_path) and os.path.isfile(gltf_output_path)
    return found

def inject_export_path_into_internal_blueprints(internal_blueprints, blueprints_path, gltf_extension, settings):
    export_materials_library = getattr(settings.auto_export, "export_materials_library")
    # FIXME: duplicate of materials stuff
    export_gltf_extension = getattr(settings, "export_gltf_extension", ".glb")
    materials_path =  getattr(settings, "materials_path")
    current_project_name = Path(bpy.context.blend_data.filepath).stem
    materials_library_name = f"{current_project_name}_materials"
    materials_exported_path = os.path.join(materials_path, f"{materials_library_name}{export_gltf_extension}")

    for blueprint in internal_blueprints:
        blueprint_exported_path = os.path.join(blueprints_path, f"{blueprint.name}{gltf_extension}")
        # print("injecting blueprint path", blueprint_exported_path, "for", blueprint.name)
        blueprint.collection["export_path"] = blueprint_exported_path
        if export_materials_library:
            blueprint.collection["materials_path"] = materials_exported_path


def inject_blueprints_list_into_level_scene(scene, blueprints_data, settings):
    project_root_path = getattr(settings, "project_root_path")
    assets_path = getattr(settings,"assets_path")
    levels_path = getattr(settings,"levels_path")
    blueprints_path = getattr(settings, "blueprints_path")
    export_gltf_extension = getattr(settings, "export_gltf_extension")

    # print("injecting assets/blueprints data into scene")
    assets_list_name = f"assets_list_{scene.name}_components"
    assets_list_data = {}

    blueprint_instance_names_for_scene = blueprints_data.blueprint_instances_per_level_scene.get(scene.name, None)
    blueprint_assets_list = []
    if blueprint_instance_names_for_scene:
        for blueprint_name in blueprint_instance_names_for_scene:
            blueprint = blueprints_data.blueprints_per_name.get(blueprint_name, None)
            if blueprint is not None: 
                #print("BLUEPRINT", blueprint)
                blueprint_exported_path = None
                if blueprint.local:
                    blueprint_exported_path = os.path.join(blueprints_path, f"{blueprint.name}{export_gltf_extension}")
                else:
                    # get the injected path of the external blueprints
                    blueprint_exported_path = blueprint.collection['Export_path'] if 'Export_path' in blueprint.collection else None
                    #print("foo", dict(blueprint.collection))
                if blueprint_exported_path is not None:
                    blueprint_assets_list.append({"name": blueprint.name, "path": blueprint_exported_path, "type": "MODEL", "internal": True})
                

  

    assets_list_name = f"assets_{scene.name}"
    scene["assets"] = json.dumps(blueprint_assets_list)

    #print("blueprint assets", blueprint_assets_list)

def remove_blueprints_list_from_level_scene(scene):
    assets_list = None
    assets_list_name = f"assets_list_{scene.name}_components"

    for object in scene.objects:
        if object.name == assets_list_name:
            assets_list = object
    if assets_list is not None:
        bpy.data.objects.remove(assets_list, do_unlink=True)
