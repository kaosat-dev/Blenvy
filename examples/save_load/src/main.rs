use std::any::TypeId;

use bevy::{prelude::*, utils::hashbrown::HashSet};
use blenvy::{AddToGameWorld, BlenvyPlugin, BluePrintBundle, BlueprintInfo, Dynamic, DynamicBlueprintInstance, GameWorldTag, HideUntilReady, SaveRequest, SpawnBlueprint};
use rand::Rng;

// mod game;
// use game::*;

mod component_examples;
use component_examples::*;

fn main() {
    App::new()
        .add_plugins((
            DefaultPlugins.set(AssetPlugin::default()),
            BlenvyPlugin {
                save_component_filter: SceneFilter::Allowlist(HashSet::from([
                    TypeId::of::<Name>(),
                    TypeId::of::<Transform>(),
                    //TypeId::of::<Velocity>(),
                    TypeId::of::<InheritedVisibility>(),
                    TypeId::of::<Camera>(),
                    TypeId::of::<Camera3d>(),
                    //TypeId::of::<Tonemapping>(),
                    //TypeId::of::<CameraTrackingOffset>(),
                    TypeId::of::<Projection>(),
                    //TypeId::of::<CameraRenderGraph>(),
                    //TypeId::of::<Frustum>(),
                    TypeId::of::<GlobalTransform>(),
                    //TypeId::of::<VisibleEntities>(),
                    //TypeId::of::<Pickable>(),
                ])),
                ..Default::default()
            },
            // our custom plugins
            // GamePlugin,           // specific to our game
            ComponentsExamplesPlugin, // Showcases different type of components /structs
        ))

        .add_systems(Startup, setup_game)
        .add_systems(Update, (spawn_blueprint_instance, move_movers, save_game, load_game))

        .run();
}

// this is how you setup & spawn a level from a blueprint
fn setup_game(
    mut commands: Commands,
) {

    // here we spawn our game world/level, which is also a blueprint !
    commands.spawn((
        BlueprintInfo::from_path("levels/World.glb"), // all we need is a Blueprint info...
        SpawnBlueprint, // and spawnblueprint to tell blenvy to spawn the blueprint now
        HideUntilReady, // only reveal the level once it is ready
        GameWorldTag,
    ));

     // here we spawn our game world/level, which is also a blueprint !
     commands.spawn((
        BlueprintInfo::from_path("levels/World_dynamic.glb"), // all we need is a Blueprint info...
        SpawnBlueprint, // and spawnblueprint to tell blenvy to spawn the blueprint now
        HideUntilReady, // only reveal the level once it is ready
    ));
}

// you can also spawn blueprint instances at runtime
fn spawn_blueprint_instance(
    keycode: Res<ButtonInput<KeyCode>>,
    mut commands: Commands,
) {
    if keycode.just_pressed(KeyCode::KeyT) {
        // random position
        let mut rng = rand::thread_rng();
        let range = 5.5;
        let x: f32 = rng.gen_range(-range..range);
        let y: f32 = rng.gen_range(-range..range);

        // random name
        let name_index: u64 = rng.gen();

        commands
            .spawn((
                BlueprintInfo::from_path("blueprints/test.glb"),
                SpawnBlueprint,
                DynamicBlueprintInstance,
                bevy::prelude::Name::from(format!("test{}", name_index)),
                HideUntilReady,
                AddToGameWorld,
                TransformBundle::from_transform(Transform::from_xyz(x, 2.0, y)),
            ));
    }
}

fn move_movers(
    mut movers: Query<(&mut Transform), With<Dynamic>>
) {
    for mut transform in movers.iter_mut(){
        println!("moving dynamic entity");
        transform.translation.x += 0.01;
    }
}

fn save_game(
    keycode: Res<ButtonInput<KeyCode>>,
    mut save_requests: EventWriter<SaveRequest>,
) {
    if keycode.just_pressed(KeyCode::KeyS) {
        save_requests.send(SaveRequest {
            path: "scenes/save.scn.ron".into(),
        });
    }
}

/* 
pub fn request_save(
    mut save_requests: EventWriter<SaveRequest>,
    keycode: Res<ButtonInput<KeyCode>>,

    current_state: Res<State<GameState>>,
    mut next_game_state: ResMut<NextState<GameState>>,
) {
    if keycode.just_pressed(KeyCode::KeyS)
        && (current_state.get() != &GameState::InLoading)
        && (current_state.get() != &GameState::InSaving)
    {
        next_game_state.set(GameState::InSaving);
        save_requests.send(SaveRequest {
            path: "save.scn.ron".into(),
        });
    }
}*/



fn load_game(
    keycode: Res<ButtonInput<KeyCode>>,
) {
    if keycode.just_pressed(KeyCode::KeyL) {

    }
}
