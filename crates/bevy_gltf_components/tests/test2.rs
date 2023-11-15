use bevy::{prelude::*, gltf::{GltfPlugin, Gltf}, scene::ScenePlugin, pbr::PbrPlugin, render::RenderPlugin, core_pipeline::CorePipelinePlugin};
use bevy_gltf_components::ComponentsFromGltfPlugin;

#[derive(Resource)]
pub struct MyGltf(pub Handle<Gltf>);

fn setup(
    mut commands: Commands, 
    asset_server: Res<AssetServer>,
) {
    println!("setting up loading");
    commands.insert_resource(MyGltf(asset_server.load("models/level1.glb")));
}

fn foo(
    mut asset_event_reader: EventReader<AssetEvent<Gltf>>,
){
    if let Some(asset_event) = asset_event_reader.read().next() {
        println!("asset event {:?}",asset_event);
        match asset_event {
            AssetEvent::Added { id: _ } => {
                info!("GLTF Added");
            },
            AssetEvent::LoadedWithDependencies { id: _ } => {
                info!("GLTF loaded");
            },
            _ => ()
        }
    }
}
fn bruteforce(
    foo: Res<MyGltf>,
    asset_server: Res<AssetServer>,
){
    let load_state = asset_server.get_load_state(foo.0.id());
    println!("checking load state {:?}", load_state);

}

#[test]
fn main() {
    // Setup app
    let mut app = App::new();
    app
        // .register_type::<BasicTest>()
        // .register_type::<UnitTest>()
        /* .add_plugins((
            MinimalPlugins,
            AssetPlugin::default(),
            CorePipelinePlugin::default(),

            RenderPlugin::default(),

            PbrPlugin::default(),
            GltfPlugin::default(),
            ScenePlugin::default(),

            HierarchyPlugin::default(),
            TransformPlugin::default(),
            
        ))*/
        .add_plugins(DefaultPlugins)

        .add_plugins(ComponentsFromGltfPlugin)
        
        .add_systems(Startup, setup)
        .add_systems(Update, foo)
        .add_systems(Update, bruteforce)

        .run()
        ;

    /*app.update();
    app.update();
    app.update();
    app.update();
    app.update();
    app.update();
    loop {
        // println!("foo {:?}", app.world.resource::<Added<MyGltf>>().clone());
        app.update();
    }*/

}