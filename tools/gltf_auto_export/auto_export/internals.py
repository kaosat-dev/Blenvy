import bpy

class SceneLink(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="")
    scene: bpy.props.PointerProperty(type=bpy.types.Scene)

class SceneLinks(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="List of scenes to export", default="Unknown")
    items: bpy.props.CollectionProperty(type = SceneLink)

class CUSTOM_PG_sceneName(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    display: bpy.props.BoolProperty()

class CollectionToExport(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="")

class BlueprintsToExport(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="List of collections to export", default="Unknown")
    items: bpy.props.CollectionProperty(type = CollectionToExport)


