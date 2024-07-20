# Export

## Materials

You can enable this option to automatically generate a **material library** files that combines all the materials in use in your blueprints.

![material_library](./docs/blender_addon_materials2.png)

Since each blueprint is normally a completely independant gltf file, without this option, if you have a material with a large texture for example, 
**ALL** of your blueprints using that material will embed that large texture, leading to **significant bloat & memory use**.

- When this option is enabled, you get a single material library per Blender project, and a **MaterialInfo** component is inserted into each object using a material.
- The correct material will then be inserted on the Bevy side (that loads any number of material libraries that you need) into the correct mesh
- Only one material per object is supported at this stage, ie the last material slot's material is the one that is going to be used

![material_library](./docs/blender_addon_materials.png)

TLDR: Use this option to make sure that each blueprint file does not contain a copy of the same materials 


## Technical details

### Internal process (simplified)

This is the internal logic of the export process with blueprints (simplified)

![process](./docs/process.svg)

ie this is an example scene...

![](./docs/workflow_original.jpg)

and what actually gets exported for the level scene/world/level

![](./docs/workflow_empties.jpg)

all collections instances replaced with empties, and all those collections exported to gltf files as seen above