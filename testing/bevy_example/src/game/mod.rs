pub mod in_game;
use std::{
    fs::{self},
    time::Duration,
};

use bevy_gltf_blueprints::{AnimationPlayerLink, BlueprintName};
pub use in_game::*;

use bevy::{
    prelude::*, render::view::screenshot::ScreenshotManager, time::common_conditions::on_timer,
    window::PrimaryWindow,
};
use bevy_gltf_worlflow_examples_common::{AppState, GameState};

use crate::{TupleTestF32, UnitTest};

fn start_game(mut next_app_state: ResMut<NextState<AppState>>) {
    next_app_state.set(AppState::AppLoading);
}

// if the export from Blender worked correctly, we should have animations (simplified here by using AnimationPlayerLink)
// if the export from Blender worked correctly, we should have an Entity called "Cylinder" that has two components: UnitTest, TupleTestF32
// if the export from Blender worked correctly, we should have an Entity called "Blueprint4_nested" that has a child called "Blueprint3" that has a "BlueprintName" component with value Blueprint3

fn validate_export(
    parents: Query<&Parent>,
    children: Query<&Children>,
    names: Query<&Name>,
    blueprints: Query<(Entity, &Name, &BlueprintName)>,
    animation_player_links: Query<(Entity, &AnimationPlayerLink)>,
    exported_cylinder: Query<(Entity, &Name, &UnitTest, &TupleTestF32)>,
    empties_candidates: Query<(Entity, &Name, &GlobalTransform)>,
) {
    let animations_found = !animation_player_links.is_empty();

    let mut cylinder_found = false;
    if let Ok(nested_cylinder) = exported_cylinder.get_single() {
        let parent_name = names
            .get(parents.get(nested_cylinder.0).unwrap().get())
            .unwrap();
        cylinder_found = parent_name.to_string() == *"Cube.001"
            && nested_cylinder.1.to_string() == *"Cylinder"
            && nested_cylinder.3 .0 == 75.1;
    }

    let mut nested_blueprint_found = false;
    for (entity, name, blueprint_name) in blueprints.iter() {
        if name.to_string() == *"Blueprint4_nested" && blueprint_name.0 == *"Blueprint4_nested" {
            if let Ok(cur_children) = children.get(entity) {
                for child in cur_children.iter() {
                    if let Ok((_, child_name, child_blueprint_name)) = blueprints.get(*child) {
                        if child_name.to_string() == *"Blueprint3"
                            && child_blueprint_name.0 == *"Blueprint3"
                        {
                            nested_blueprint_found = true;
                        }
                    }
                }
            }
        }
    }

    let mut empty_found = false;
    for (_, name, _) in empties_candidates.iter() {
        if name.to_string() == *"Empty" {
            empty_found = true;
            break;
        }
    }

    fs::write(
        "bevy_diagnostics.json",
        format!(
            "{{ \"animations\": {},  \"cylinder_found\": {} ,  \"nested_blueprint_found\": {}, \"empty_found\": {} }}",
            animations_found, cylinder_found, nested_blueprint_found, empty_found
        ),
    )
    .expect("Unable to write file");
}

fn generate_screenshot(
    main_window: Query<Entity, With<PrimaryWindow>>,
    mut screenshot_manager: ResMut<ScreenshotManager>,
) {
    screenshot_manager
        .save_screenshot_to_disk(main_window.single(), "screenshot.png")
        .unwrap();
}

fn exit_game(mut app_exit_events: ResMut<Events<bevy::app::AppExit>>) {
    app_exit_events.send(bevy::app::AppExit);
}

pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Update, (spawn_test).run_if(in_state(GameState::InGame)))
            .add_systems(Update, validate_export)
            .add_systems(Update, generate_screenshot.run_if(on_timer(Duration::from_secs_f32(0.2)))) // TODO: run once
            .add_systems(OnEnter(AppState::MenuRunning), start_game)
            .add_systems(OnEnter(AppState::AppRunning), setup_game)
            .add_systems(
                Update,
                exit_game.run_if(on_timer(Duration::from_secs_f32(0.5))),
            ) // shut down the app after this time
            ;
    }
}
