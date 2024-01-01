[![Crates.io](https://img.shields.io/crates/v/bevy_gltf_blueprints)](https://crates.io/crates/bevy_gltf_blueprints)
[![Docs](https://img.shields.io/docsrs/bevy_gltf_blueprints)](https://docs.rs/bevy_gltf_blueprints/latest/bevy_gltf_blueprints/)
[![License](https://img.shields.io/crates/l/bevy_gltf_blueprints)](https://github.com/kaosat-dev/Blender_bevy_components_workflow/blob/main/crates/bevy_gltf_blueprints/License.md)
[![Bevy tracking](https://img.shields.io/badge/Bevy%20tracking-released%20version-lightblue)](https://github.com/bevyengine/bevy/blob/main/docs/plugins_guidelines.md#main-branch-tracking)

# bevy_gltf_blueprints

Built upon [bevy_gltf_components](https://crates.io/crates/bevy_gltf_components) this crate adds the ability to define Blueprints/Prefabs for [Bevy](https://bevyengine.org/) inside gltf files and spawn them in Bevy.

* Allows you to create lightweight levels, where all assets are different gltf files and loaded after the main level is loaded
* Allows you to spawn different entities from gtlf files at runtime in a clean manner, including simplified animation support !

A blueprint is a set of **overrideable** components + a hierarchy: ie 

    * just a Gltf file with Gltf_extras specifying components 
    * a component called BlueprintName

Particularly useful when using [Blender](https://www.blender.org/) as an editor for the [Bevy](https://bevyengine.org/) game engine, combined with the [Blender plugin](https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/tools/gltf_auto_export) that does a lot of the work for you 


## Usage

Here's a minimal usage example:

```toml
# Cargo.toml
[dependencies]
bevy="0.12"
bevy_gltf_blueprints = { version = "0.5"} 

```

```rust no_run
use bevy::prelude::*;
use bevy_gltf_blueprints::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugins(BlueprintsPlugin)

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

##  Installation

Add the following to your `[dependencies]` section in `Cargo.toml`:

```toml
bevy_gltf_blueprints = "0.5"
```

Or use `cargo add`:

```toml
cargo add bevy_gltf_blueprints
```

## Setup

```rust no_run
use bevy::prelude::*;
use bevy_gltf_blueprints::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugin(BlueprintsPlugin)

        .run();
}

```

you may want to configure your "library"/"blueprints" settings:

```rust no_run
use bevy::prelude::*;
use bevy_gltf_blueprints::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugin(
             BlueprintsPlugin{
                library_folder: "advanced/models/library".into() // replace this with your blueprints library path , relative to the assets folder,
                format: GltfFormat::GLB,// optional, use either  format: GltfFormat::GLB, or  format: GltfFormat::GLTF, or  ..Default::default() if you want to keep the default .glb extension, this sets what extensions/ gltf files will be looked for by the library
                aabbs: true, // defaults to false, enable this to automatically calculate aabb for the scene/blueprint
                material_library: true,  // defaults to false, enable this to enable automatic injection of materials from material library files
                material_library_folder: "materials".into() //defaults to "materials" the folder to look for for the material files
                ..Default::default()
            }
        )
        .run();
}

```

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

see https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/bevy_gltf_blueprints/basic for how to set it up correctly



## Animation

```bevy_gltf_blueprints``` provides some lightweight helpers to deal with animations stored in gltf files

 * an ```Animations``` component that gets inserted into spawned (root) entities that contains a hashmap of all animations contained inside that entity/gltf file .
 (this is a copy of the ```named_animations``` inside Bevy's gltf structures )
 * an ```AnimationPlayerLink``` component that gets inserted into spawned (root) entities, to make it easier to trigger/ control animations than it usually is inside Bevy + Gltf files

The workflow for animations is as follows:
* create a gltf file with animations (using Blender & co) as you would normally do
* inside Bevy, use the ```bevy_gltf_blueprints``` boilerplate (see sections above), no specific setup beyond that is required
* to control the animation of an entity, you need to query for entities that have both ```AnimationPlayerLink``` and ```Animations``` components (added by ```bevy_gltf_blueprints```) AND entities with the ```AnimationPlayer``` component
 
For example:

```rust no_run
// example of changing animation of entities based on proximity to the player, for "fox" entities (Tag component)
pub fn animation_change_on_proximity_foxes(
    players: Query<&GlobalTransform, With<Player>>,
    animated_foxes: Query<(&GlobalTransform, &AnimationPlayerLink, &Animations ), With<Fox>>,

    mut animation_players: Query<&mut AnimationPlayer>,

){
    for player_transforms in players.iter() {
        for (fox_tranforms, link, animations) in animated_foxes.iter() {
            let distance = player_transforms
                .translation()
                .distance(fox_tranforms.translation());
            let mut anim_name = "Walk"; 
            if distance < 8.5 {
                anim_name = "Run"; 
            }
            else if distance >= 8.5 && distance < 10.0{
                anim_name = "Walk";
            }
            else if distance >= 10.0 && distance < 15.0{
                anim_name = "Survey";
            }
            // now play the animation based on the chosen animation name
            let mut animation_player = animation_players.get_mut(link.0).unwrap();
            animation_player.play_with_transition(
                animations.named_animations.get(anim_name).expect("animation name should be in the list").clone(), 
                Duration::from_secs(3)
            ).repeat();
        }
    }
}
```

see https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/animation for how to set it up correctly

particularly from https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/animation/game/in_game.rs#86
onward 


## Materials

You have the option of using "material libraries" to share common textures/materials between blueprints, in order to avoid asset & memory bloat:

Ie for example without this option, 56 different blueprints using the same material with a large texture would lead to the material/texture being embeded
56 times !!


you can configure this with the settings:
```rust
material_library: true  // defaults to false, enable this to enable automatic injection of materials from material library files
material_library_folder: "materials".into() //defaults to "materials" the folder to look for for the material files
```

> Important! you must take care of preloading your material librairy gltf files in advance, using for example ```bevy_asset_loader```since 
```bevy_gltf_blueprints``` currently does NOT take care of loading those at runtime


see https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/materials for how to set it up correctly

Generating optimised blueprints and material libraries can be automated using the latests version of the [Blender plugin](https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/tools/gltf_auto_export)

## Examples

https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/basic

https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/basic_xpbd_physics

https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/basic_scene_components

https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/animation

https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/multiple_levels

https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/materials

https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/nested_blueprints

https://github.com/kaosat-dev/Blender_bevy_components_workflow/tree/main/examples/multiple_levels_multiple_blendfiles


## Compatible Bevy versions

The main branch is compatible with the latest Bevy release, while the branch `bevy_main` tries to track the `main` branch of Bevy (PRs updating the tracked commit are welcome).

Compatibility of `bevy_gltf_blueprints` versions:
| `bevy_gltf_blueprints` | `bevy` |
| :--                 | :--    |
| `0.3 - 0.5`         | `0.12` |
| `0.1 - 0.2`         | `0.11` |
| branch `main`       | `0.12` |
| branch `bevy_main`  | `main` |


## License

This crate, all its code, contents & assets is Dual-licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](./LICENSE_APACHE.md) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](./LICENSE_MIT.md) or https://opensource.org/licenses/MIT)