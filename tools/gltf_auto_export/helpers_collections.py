import bpy
from .helpers import traverse_tree

# returns the list of the collections in use for a given scene
# FIXME: this should also look into sub collections
def get_used_collections(scene): 
    root_collection = scene.collection 

    scene_objects = [o for o in root_collection.objects]
    collection_names = set()
    used_collections = []
    for object in scene_objects:
        #print("object ", object)
        if object.instance_type == 'COLLECTION':
            collection_name = object.instance_collection.name
            if not collection_name in collection_names: 
                collection_names.add(collection_name)
                used_collections.append(object.instance_collection)

    #print("scene objects", scene_objects) 
    return (collection_names, used_collections)

# gets all collections that should ALWAYS be exported to their respective gltf files, even if they are not used in the main scene/level
def get_marked_collections(scene, addon_prefs):
    export_marked_assets = getattr(addon_prefs,"export_marked_assets")

    # print("checking library for marked collections")
    root_collection = scene.collection
    marked_collections = []
    collection_names = []
    for collection in traverse_tree(root_collection):
        if 'AutoExport' in collection and collection['AutoExport'] == True:
            marked_collections.append(collection)
            collection_names.append(collection.name)
        # if you have marked collections as assets you can auto export them too
        if export_marked_assets and collection.asset_data is not None: 
            marked_collections.append(collection)
            collection_names.append(collection.name)
    return (collection_names, marked_collections)

# gets all collections within collections that might also be relevant
def get_sub_collections(collections, parent, children_per_collection):
    collection_names = set()
    used_collections = []
    

    for root_collection in collections:
        node = Node(name=root_collection.name, parent=parent)
        parent.children.append(node)

      
        #print("root collection", root_collection.name)
        for collection in traverse_tree(root_collection): # TODO: filter out COLLECTIONS that have the flatten flag (unlike the flatten flag on colleciton instances themselves)
            node_name = collection.name
            children_per_collection[node_name] = []
            #print("  scanning", collection.name)
            for object in collection.objects:
                #print("FLATTEN", object.name, 'Flatten' in object)
                if object.instance_type == 'COLLECTION' : # and not 'Flatten' in object: 
                    collection_name = object.instance_collection.name
                    (sub_names, sub_collections) = get_sub_collections([object.instance_collection], node, children_per_collection)
                    if len(list(sub_names)) > 0:
                        children_per_collection[node_name]  += (list(sub_names))
                    #print("   found sub collection in use", object.name, object.instance_collection)


                    if not collection_name in collection_names: 
                        collection_names.add(collection_name)
                        used_collections.append(object.instance_collection)
                        collection_names.update(sub_names)

        #for sub in traverse_tree(root_collection):
    return (collection_names, used_collections)

# FIXME: get rid of this, ugh
def flatten_collection_tree(node, children_per_collection):
    children_per_collection[node.name] = []
    for child in node.children:
        if not node.name in children_per_collection[node.name]:
            children_per_collection[node.name].append(child.name)
        flatten_collection_tree(child, children_per_collection)
    children_per_collection[node.name] = list(set( children_per_collection[node.name]))
       

class Node :
    def __init__(self, name="", parent=None):
      self.name = name
      self.children = []
      self.changed = False
      self.parent = parent
      return
    def __str__(self):
        children = list(map(lambda child: str(child), self.children))
        return "name: " +self.name + ", children:" + str(children)
    
# get exportable collections from lists of mains scenes and lists of library scenes
def get_exportable_collections(main_scenes, library_scenes, addon_prefs): 
    export_nested_blueprints = getattr(addon_prefs,"export_nested_blueprints")

    all_collections = []
    all_collection_names = []
    root_node = Node()
    root_node.name = "root"
    children_per_collection = {}


    for main_scene in main_scenes:
        (collection_names, collections) = get_used_collections(main_scene)
        all_collection_names = all_collection_names + list(collection_names)
        all_collections = all_collections + collections
    for library_scene in library_scenes:
        marked_collections = get_marked_collections(library_scene, addon_prefs)
        all_collection_names = all_collection_names + marked_collections[0]
        all_collections = all_collections + marked_collections[1]

    if export_nested_blueprints:
        (collection_names, collections) = get_sub_collections(all_collections, root_node, children_per_collection)
        all_collection_names = all_collection_names + list(collection_names)
        children_per_collection = {}
        flatten_collection_tree(root_node, children_per_collection)
        #print("ROOT NODE", children_per_collection) #

    return (all_collection_names, children_per_collection)

def get_collections_per_scene(collection_names, library_scenes): 
    collections_per_scene = {}
    for scene in library_scenes:
        root_collection = scene.collection
        for cur_collection in traverse_tree(root_collection):
            if cur_collection.name in collection_names:
                if not scene.name in collections_per_scene:
                    collections_per_scene[scene.name] = []
                collections_per_scene[scene.name].append(cur_collection.name)
                
    return collections_per_scene

def get_collections_in_library(library_scenes):
    """all_collections = []
    all_collection_names = []
    for main_scene in main_scenes:
        (collection_names, collections) = get_used_collections(main_scene)
        all_collection_names = all_collection_names + list(collection_names)
        all_collections = all_collections + collections"""

    # now that we have the collections that are in use by collection instances, check if those collections are actully present in the library scenes
    collections = []
    collection_names = []
    for library_scene in library_scenes:
        root_collection = library_scene.collection
     
        for collection in traverse_tree(root_collection):
            collections.append(collection)
            collection_names.append(collection.name)
    return collection_names


def get_collection_hierarchy(root_col, levels=1):
    """Read hierarchy of the collections in the scene"""
    level_lookup = {}
    def recurse(root_col, parent, depth):
        if depth > levels: 
            return
        if isinstance(parent,  bpy.types.Collection):
            level_lookup.setdefault(parent, []).append(root_col)
        for child in root_col.children:
            recurse(child, root_col,  depth + 1)
    recurse(root_col, root_col.children, 0)
    return level_lookup

# the active collection is a View Layer concept, so you actually have to find the active LayerCollection
# which must be done recursively
def find_layer_collection_recursive(find, col):
    # print("root collection", col)
    for c in col.children:
        # print("child collection", c)
        if c.collection == find:
            return c
    return None

#Recursivly transverse layer_collection for a particular name
def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found

def find_collection_ascendant_target_collection(collection_parents, target_collections, collection):
    if collection == None:
        return None
    if collection in target_collections:
        return collection
    parent = collection_parents[collection]
    return find_collection_ascendant_target_collection(collection_parents, target_collections, parent)
   
