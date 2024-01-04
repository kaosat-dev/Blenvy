use bevy::pbr::{Clusters, VisiblePointLights};
use bevy::reflect::TypeRegistryArc;
use bevy::render::camera::CameraRenderGraph;
use bevy::render::view::VisibleEntities;
use bevy::tasks::IoTaskPool;
use bevy::transform::commands;
use bevy::utils::HashSet;
use bevy::{gltf::GltfExtras, prelude::*};
use bevy_gltf_blueprints::{BlueprintName, SpawnHere, Save};
use bevy_rapier3d::dynamics::Velocity;
use bevy_rapier3d::prelude::RigidBody;
use json::camera::Type;
use json::validation::{Checked, Validate};
use std::any::{Any, TypeId};
use std::fs::{File, self};
use std::io::Write;

use crate::core::physics::Collider;
use crate::core::save_load::Dynamic;
use crate::game::{Pickable, Player};

const NEW_SCENE_FILE_PATH: &str = "save.scn.ron";

use gltf_json as json;
use serde_json::value::{to_raw_value, RawValue};
use serde::Serialize;

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
enum Output {
    /// Output standard glTF.
    Standard,

    /// Output binary glTF.
    Binary,
}
#[derive(Serialize)]
struct MyExtraData {
    a: u32,
    b: u32,
    BlueprintName: String,
    SpawnHere: String,
}

#[derive(Component, Event)]
pub struct SaveRequest {
    pub path: String,
}

pub fn should_save(
     keycode: Res<Input<KeyCode>>,
    //save_requested_events: EventReader<SaveRequest>,
) -> bool {
    //return save_requested_events.len() > 0;

    return keycode.just_pressed(KeyCode::S)
}

/* 
pub fn serialize_gltf_inner<S>(serialize: S) -> Result<String, json::Error>
where
    S: Serialize,
{
    let pretty_config = ron::ser::PrettyConfig::default()
        .indentor("  ".to_string())
        .new_line("\n".to_string());
    ron::ser::to_string_pretty(&serialize, pretty_config)
}*/

pub fn serialize_gltf(scene:&DynamicScene, registry: &TypeRegistryArc) {

}

pub fn prepare_save_game(
    saveables: Query<(Entity), With<Dynamic>>,
    mut commands: Commands,
){
    for entity in saveables.iter(){
        println!("PREPARING SAVE");
        commands.entity(entity).insert(SpawnHere);
    }
}
pub fn save_game(
    world: &mut World,
    // save_requested_events: EventReader<SaveRequest>,
) {
    info!("saving");
    // world.
    /*for bli in save_requested_events.iter(){
        println!("SAAAAVE TO THISSSSS {:?}", bli.path)
    }*/

    let saveable_entities: Vec<Entity> = world
        .query_filtered::<Entity, With<Dynamic>>()
        .iter(world)
        .collect();

    /*let static_entities: Vec<Entity> = world
    .query_filtered::<Entity, Without<Saveable>>()
    .iter(world)
    .collect();*/
    println!("saveable entities {}", saveable_entities.len());
    for ent in saveable_entities.iter() {
        // ent.apply(value)
    }

    // we need         "bevy_gltf_blueprints::spawn_from_blueprints::SpawnHere": (),

    let components = HashSet::from([
        TypeId::of::<Name>(),
        TypeId::of::<Transform>(), 
        TypeId::of::<Velocity>() , 
        TypeId::of::<BlueprintName>(),
        TypeId::of::<SpawnHere>(),
        TypeId::of::<Dynamic>()

        ]);

    let filter = SceneFilter::Allowlist(components);
        

    let mut scene_builder = DynamicSceneBuilder::from_world(world).with_filter(filter);

    let dyn_scene = scene_builder
        
        
        /* .allow::<Transform>()
        .allow::<Velocity>()
        .allow::<BlueprintName>()*/

        /* .deny::<Children>()
        .deny::<Parent>()
        .deny::<InheritedVisibility>()
        .deny::<Visibility>()
        .deny::<GltfExtras>()
        .deny::<GlobalTransform>()
        .deny::<Collider>()
        .deny::<RigidBody>()
        .deny::<Saveable>()
        // camera stuff
        .deny::<Camera>()
        .deny::<CameraRenderGraph>()
        .deny::<Camera3d>()
        .deny::<Clusters>()
        .deny::<VisibleEntities>()
        .deny::<VisiblePointLights>()
        //.deny::<HasGizmoMarker>()
        */
        .extract_entities(saveable_entities.into_iter())
        .build();

    let serialized_scene = dyn_scene
        .serialize_ron(world.resource::<AppTypeRegistry>())
        .unwrap();

    let mut root = gltf_json::Root::default();

    // unfortunatly, not available yet
    /*let node = root.push(json::Node {
        //mesh: Some(mesh),
        ..Default::default()
    });

    root.push(json::Scene {
        extensions: Default::default(),
        extras: Default::default(),
        name: None,
        nodes: vec![node],
    });*/





    let camera = json::camera::Perspective{
        aspect_ratio: Some(0.5),
        yfov: 32.0,
        zfar: Some(30.),
        znear: 0.0,
        extensions: None,
        extras: None
    };
    /*let camera = json::Camera{
        name:Some("Camera".into()),
        orthographic: None,
        perspective:None,
        extensions: None,
        extras: None,
        type_: Checked<Type::Perspective>,
    };*/
    let gna = to_raw_value(&MyExtraData { a: 1, b: 2, BlueprintName: "Foo".into(), SpawnHere:"".into() }).unwrap() ;
    let node = json::Node {
        camera: None,//Some(camera),
        children: None,
        extensions: None,
        extras: Some(gna),
        matrix: None,
        mesh:None,
        name: Some("yeah".into()),
        rotation: None,
        scale: None,
        translation: Some([0.5, 10.0 ,-100.]),
        skin: None,
        weights: None
        // mesh: Some(json::Index::new(0)),
        //..Default::default()
    };
   
    let root = json::Root {
        accessors: vec![], //[positions, colors],
        buffers: vec![],
        buffer_views: vec![],
        meshes: vec![],
        nodes: vec![node],
        scenes: vec![json::Scene {
            extensions: Default::default(),
            extras: Default::default(),
            name: Some("Foo".to_string()),
            nodes: vec![json::Index::new(0)],
        }],
        ..Default::default()
    };




    let gltf_save_name = "test.gltf";
    let writer = fs::File::create(format!("assets/scenes/{gltf_save_name}") ).expect("I/O error");
    json::serialize::to_writer_pretty(writer, &root).expect("Serialization error");

    // let bin = to_padded_byte_vector(triangle_vertices);
    // let mut writer = fs::File::create("triangle/buffer0.bin").expect("I/O error");
    // writer.write_all(&bin).expect("I/O error");

    
    #[cfg(not(target_arch = "wasm32"))]
    IoTaskPool::get()
        .spawn(async move {
            // Write the scene RON data to file
            File::create(format!("assets/scenes/{NEW_SCENE_FILE_PATH}"))
                .and_then(|mut file| file.write(serialized_scene.as_bytes()))
                .expect("Error while writing scene to file");



        })
        .detach();
}
