[![Crates.io](https://img.shields.io/crates/v/bevy_gltf_blueprints)](https://crates.io/crates/bevy_gltf_blueprints)
[![Docs](https://img.shields.io/docsrs/bevy_gltf_blueprints)](https://docs.rs/bevy_gltf_blueprints/latest/bevy_gltf_blueprints/)
[![License](https://img.shields.io/crates/l/bevy_gltf_blueprints)](https://github.com/kaosat-dev/Blender_bevy_components_worklflow/blob/main/crates/bevy_gltf_blueprints/License.md)
[![Bevy tracking](https://img.shields.io/badge/Bevy%20tracking-released%20version-lightblue)](https://github.com/bevyengine/bevy/blob/main/docs/plugins_guidelines.md#main-branch-tracking)

# bevy_gltf_blueprints

Built upon [bevy_gltf_components](https://crates.io/crates/bevy_gltf_components) this crate adds the ability to define Blueprints/Prefabs for [Bevy](https://bevyengine.org/) inside gltf files and spawn them in Bevy.

A blueprint is a set of **overrideable** components + a hierarchy: ie 

    * just a Gltf file with Gltf_extras specifying components 
    * a component called BlueprintName

Particularly useful when using [Blender](https://www.blender.org/) as an editor for the [Bevy](https://bevyengine.org/) game engine, combined with the [Blender plugin](https://github.com/kaosat-dev/Blender_bevy_components_worklflow/tree/main/tools/gltf_auto_export) that does a lot of the work for you 


## Usage

Here's a minimal usage example:

```toml
# Cargo.toml
[dependencies]
bevy_gltf_blueprints = { version = "0.1.0"} 

```

```rust no_run
use bevy::prelude::*;
use bevy_gltf_blueprints::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugin(BlueprintsPlugin)

        .run();
}

// not shown here: any other setup that is not specific to blueprints

fn spawn_blueprint(
    mut commands: Commands,
    keycode: Res<Input<KeyCode>>,
){
    if keycode.just_pressed(KeyCode::S) {
        let new_entity = commands.spawn((
            BlueprintName("Health_Pickup".to_string()), // mandatory !!
            SpawnHere, // mandatory !!
            TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)), // VERY important !!
            // any other component you want to insert
        ));
    }
}
```

## Setup

- configure your "library"/"blueprints" path: 
    advanced/models/library/

## Spawning entities from blueprints

You can spawn entities from blueprints like this:
```rust no_run
commands.spawn((
    BlueprintName("Health_Pickup".to_string()), // mandatory !!
    SpawnHere, // mandatory !!
    TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)), // VERY important !!
    // any other component you want to insert
))

``` 

Once spawning of the actual entity is done, the spawned Blueprint will be *gone/merged* with the contents of Blueprint !

> Important :
you can **add** or **override** components present inside your Blueprint when spawning the BluePrint itself: ie

### Adding components not specified inside the blueprint

you can just add any additional components you need when spawning :

```rust no_run
commands.spawn((
    BlueprintName("Health_Pickup".to_string()),
    SpawnHere,
    TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
    // from Rapier/bevy_xpbd: this means the entity will also have a velocity component when inserted into the world
    Velocity {
        linvel: Vec3::new(vel_x, vel_y, vel_z),
        angvel: Vec3::new(0.0, 0.0, 0.0),
      },
))

``` 
### Overriding components specified inside the blueprint

any component you specify when spawning the Blueprint that is also specified **within** the Blueprint will **override** that component in the final spawned entity

for example 
```rust no_run
commands.spawn((
    BlueprintName("Health_Pickup".to_string()),
    SpawnHere,
    TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
    HealthPowerUp(20)// if this is component is also present inside the "Health_Pickup" blueprint, that one will be replaced with this component during spawning
))

``` 

### BluePrintBundle

There is also a bundle for convenience , which just has 
 * a ```BlueprintName``` component
 * a ```SpawnHere``` component
 * a ```TransformBundle``` sub-bundle (so we know where to spawn)

[```BluePrintBundle```](./src/lib.rs#22)


## SystemSet

the ordering of systems is very important ! 

For example to replace your proxy components (stand-in components when you cannot/ do not want to use real components in the gltf file) with actual ones, which should happen **AFTER** the Blueprint based spawning, 

so ```bevy_gltf_blueprints``` provides a **SystemSet** for that purpose:[```GltfBlueprintsSet```](./src/lib.rs#16)

Typically , the order of systems should be

***bevy_gltf_components (GltfComponentsSet::Injection)*** => ***bevy_gltf_blueprints (GltfBlueprintsSet::Spawn, GltfBlueprintsSet::AfterSpawn)*** => ***replace_proxies***

see https://github.com/kaosat-dev/Blender_bevy_components_worklflow/tree/main/examples/advanced for how to set it up correctly

## Examples

https://github.com/kaosat-dev/Blender_bevy_components_worklflow/tree/main/examples/advanced

