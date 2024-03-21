pub mod in_game;
use std::{
    collections::HashMap, fs, time::Duration
};

use bevy_gltf_blueprints::{Animated, AnimationPlayerLink, Animations, BlueprintName, BlueprintsList};
pub use in_game::*;

use bevy::{
    ecs::query, gltf::Gltf, prelude::*, render::view::screenshot::ScreenshotManager, time::common_conditions::on_timer, window::PrimaryWindow
};
use bevy_gltf_worlflow_examples_common_rapier::{AppState, GameState};

use crate::{TupleTestF32, UnitTest};
use json_writer::to_json_string;

fn start_game(mut next_app_state: ResMut<NextState<AppState>>) {
    next_app_state.set(AppState::AppLoading);
}


// if the export from Blender worked correctly, we should have animations (simplified here by using AnimationPlayerLink)
// if the export from Blender worked correctly, we should have an Entity called "Blueprint4_nested" that has a child called "Blueprint3" that has a "BlueprintName" component with value Blueprint3
// if the export from Blender worked correctly, we should have a blueprints_list
// if the export from Blender worked correctly, we should have the correct tree of entities 
#[allow(clippy::too_many_arguments)]
fn validate_export(
    parents: Query<&Parent>,
    children: Query<&Children>,
    names: Query<&Name>,
    blueprints: Query<(Entity, &Name, &BlueprintName)>,
    animation_player_links: Query<(Entity, &AnimationPlayerLink)>,
    empties_candidates: Query<(Entity, &Name, &GlobalTransform)>,

    blueprints_list: Query<(Entity, &BlueprintsList)>,
    root: Query<(Entity, &Name, &Children), (Without<Parent>, With<Children>)>
) {
    let animations_found = !animation_player_links.is_empty();

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
    // check if there are blueprints_list components
    let blueprints_list_found = !blueprints_list.is_empty();

    // there should be no entity named xxx____bak as it means an error in the Blender side export process
    let mut exported_names_correct = true;
    for name in names.iter() {
        if name.to_string().ends_with("___bak") {
            exported_names_correct = false;
            break;
        }
    }

    // generate parent/child "tree"
    if !root.is_empty() {
        let root = root.single();
        let mut tree: HashMap<String, Vec<String>> = HashMap::new();

        for child in children.iter_descendants(root.0) {
            let child_name:String = names.get(child).map_or(String::from("no_name"), |e| e.to_string() ); //|e| e.to_string(), || "no_name".to_string());
            //println!("  child {}", child_name);
            let parent = parents.get(child).unwrap();
            let parent_name:String = names.get(parent.get()).map_or(String::from("no_name"), |e| e.to_string() ); //|e| e.to_string(), || "no_name".to_string());
            tree.entry(parent_name).or_default().push(child_name.clone());
        } 

        let hierarchy = to_json_string(&tree);
        fs::write(
            "bevy_hierarchy.json",
            hierarchy
        )
        .expect("unable to write hierarchy file")
    }


    fs::write(
        "bevy_diagnostics.json",
        format!(
            "{{ \"animations\": {},  \"nested_blueprint_found\": {}, \"empty_found\": {}, \"blueprints_list_found\": {}, \"exported_names_correct\": {} }}",
            animations_found, nested_blueprint_found, empty_found, blueprints_list_found, exported_names_correct
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


#[derive(Resource)]
struct MainAnimations(Vec<Handle<AnimationClip>>);

#[derive(Resource)]
struct AnimTest(Handle<Gltf>);
fn setup_main_scene_animations(
    asset_server: Res<AssetServer>,
    mut commands: Commands,
) {
    /*commands.insert_resource(MainAnimations(vec![
        asset_server.load("models/World.glb#Blueprint1_jump"),
        asset_server.load("models/World.glb#Blueprint1_move"),

        // asset_server.load("models/library/Blueprint6_animated.glb#Run"),

    ]));*/

    commands.insert_resource(AnimTest(asset_server.load("models/World.glb")));
}
fn animations(
    foo:Query<(Entity, &Name, &AnimationPlayer),(Added<AnimationPlayer>)>,
    bla:Query<(Entity, &Name, &Animated),(Added<Animated>, Without<AnimationPlayerLink>)>,
    blurp: Res<AnimTest>,

    asset_server: Res<AssetServer>,
    mut commands: Commands,
    assets_gltf: Res<Assets<Gltf>>,

) {

      
    for (entity, name, animated) in bla.iter() {
        // println!("animated stuf {:?} on entity {}", animated, name);
        
        let gltf = assets_gltf.get(&blurp.0).unwrap();

        let animations_list = animated;
        let mut matching_data = true;
        for animation_name in &animations_list.animations {
            if !gltf.named_animations.contains_key(animation_name){
                matching_data = false;
                break;
            }
        }
        if matching_data {
            println!("inserting Animations components into {} ({:?})", name, entity);
            println!("Found match {:?}", gltf.named_animations);
            commands.entity(entity).remove::<Animations>();
            commands.entity(entity).insert((
                Animations {
                    named_animations: gltf.named_animations.clone()
                }
            ));
        }
    }
    
    /*for bla in foo.iter() {
        let mut counter = 0;
        counter +=1;
        println!("found some animations {} {}", counter, bla.1);
        
        if bla.1.to_string() == "Collection".to_string(){
            /*commands.insert_resource(Animations(vec![
                asset_server.load("models/World.glb#Animation0"),
                asset_server.load("models/World.glb#Animation1"),
            ]));*/
            /*commands.entity(bla.0).insert(Animations {
                named_animations:
            })*/
        }
    }*/
}

pub struct GamePlugin;
impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Update, (spawn_test).run_if(in_state(GameState::InGame)))
            .add_systems(Update, validate_export)
            .add_systems(OnEnter(AppState::MenuRunning), start_game)
            .add_systems(OnEnter(AppState::AppRunning), setup_game)

            .add_systems(OnEnter(AppState::MenuRunning), setup_main_scene_animations)

            .add_systems(Update, animations.run_if(in_state(AppState::AppRunning)))
            /* .add_systems(Update, generate_screenshot.run_if(on_timer(Duration::from_secs_f32(0.2)))) // TODO: run once
            .add_systems(
                Update,
                exit_game.run_if(on_timer(Duration::from_secs_f32(0.5))),
            ) // shut down the app after this time*/
            ;
    }
}
