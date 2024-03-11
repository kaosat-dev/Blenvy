use std::path::{Path, PathBuf};

use bevy::{gltf::Gltf, prelude::*, utils::HashMap};

use crate::{Animations, BluePrintsConfig};

/// this is a flag component for our levels/game world
#[derive(Component)]
pub struct GameWorldTag;

/// Main component for the blueprints
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct BlueprintName(pub String);

/// flag component needed to signify the intent to spawn a Blueprint
#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct SpawnHere;

#[derive(Component)]
/// flag component for dynamically spawned scenes
pub struct Spawned;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component marking any spwaned child of blueprints ..unless the original entity was marked with the `NoInBlueprint` marker component
pub struct InBlueprint;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component preventing any spawned child of blueprints to be marked with the `InBlueprint` component
pub struct NoInBlueprint;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
// this allows overriding the default library path for a given entity/blueprint
pub struct Library(pub PathBuf);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// flag component to force adding newly spawned entity as child of game world
pub struct AddToGameWorld;

#[derive(Component)]
/// helper component, just to transfer child data
pub(crate) struct OriginalChildren(pub Vec<Entity>);


#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct BlueprintsList(pub HashMap<String,Vec<String>>);

#[derive(Reflect, Default, Debug)]
pub(crate) struct BlueprintLoadTracker{
    pub name: String,
    pub id: AssetId<Gltf>,
    pub loaded: bool,
    pub handle: Handle<Gltf>
}
#[derive(Component, Default, Debug)]
pub(crate) struct BlueprintAssetsToLoad{
    pub all_loaded: bool,
    pub asset_infos: Vec<BlueprintLoadTracker>,
    pub progress: f32
}

#[derive(Default, Debug)]
pub(crate) struct AssetLoadTracker<T:bevy::prelude::Asset>{
    pub name: String,
    pub id: AssetId<T>,
    pub loaded: bool,
    pub handle: Handle<T>
}
#[derive(Component, Default, Debug)]
pub(crate) struct AssetsToLoad<T:bevy::prelude::Asset>{
    pub all_loaded: bool,
    pub asset_infos: Vec<AssetLoadTracker<T>>,
    pub progress: f32
}


/// flag component
#[derive(Component)]
pub(crate) struct BlueprintAssetsLoaded;
/// flag component
#[derive(Component)]
pub(crate) struct BlueprintAssetsNotLoaded;

/// spawning prepare function,
/// * also takes into account the already exisiting "override" components, ie "override components" > components from blueprint
pub(crate) fn spawn_from_blueprints(
    spawn_placeholders: Query<
        (
            Entity,
            &BlueprintName,
            Option<&Parent>,
            Option<&Library>,
            Option<&Name>,
            Option<&BlueprintsList>,
        ),
        (Added<BlueprintName>, Added<SpawnHere>, Without<Spawned>),
    >,

    mut commands: Commands,
    asset_server: Res<AssetServer>,
    blueprints_config: Res<BluePrintsConfig>,
) {
    for (
        entity,
        blupeprint_name,
        original_parent,
        library_override,
        name,

        blueprints_list,
    ) in spawn_placeholders.iter()
    {
        debug!(
            "preparing to spawn {:?} for entity {:?}, id: {:?}, parent:{:?}",
            blupeprint_name.0, name, entity, original_parent
        );

        // println!("main model path {:?}", model_path);
        if blueprints_list.is_some() {
            let blueprints_list = blueprints_list.unwrap();
            // println!("blueprints list {:?}", blueprints_list.0.keys());
            let mut asset_infos:Vec<AssetLoadTracker<Gltf>> = vec![];

            for (blueprint_name, _) in blueprints_list.0.iter() {
                /*if blueprint_name == what {
                    println!("WHOLY MOLLY !")
                }*/
                // println!("library path {:?}", library_path);
                let mut library_path = &blueprints_config.library_folder; // TODO: we cannot use the overriden library path
                // FIXME: hack
                if blueprint_name == "World" {
                    library_path= &library_override.unwrap().0;
                }

                let model_file_name = format!("{}.{}", &blueprint_name, &blueprints_config.format);
                let model_path = Path::new(&library_path).join(Path::new(model_file_name.as_str()));

                let model_handle: Handle<Gltf> = asset_server.load(model_path.clone());
                let model_id = model_handle.id();
                let loaded = asset_server.is_loaded_with_dependencies(model_id);
                if !loaded {
                    asset_infos.push(AssetLoadTracker {
                        name: model_path.to_string_lossy().into(),
                        id: model_id,
                        loaded: false,
                        handle: model_handle.clone()
                    })
                }
            }
            // if not all assets are already loaded, inject a component to signal that we need them to be loaded
            if asset_infos.len() > 0 {
                commands
                .entity(entity)
                .insert(AssetsToLoad{
                    all_loaded: false,
                    asset_infos: asset_infos,
                    progress: 0.0
                    //..Default::default()
                })
                .insert(BlueprintAssetsNotLoaded);
            }else {
                commands
                .entity(entity)
                .insert(BlueprintAssetsLoaded);
            }
        }
    }
}


pub(crate) fn check_for_loaded(
    mut blueprint_assets_to_load: Query<(Entity, &mut AssetsToLoad<Gltf>), With<BlueprintAssetsNotLoaded>>,
    asset_server: Res<AssetServer>,
    mut commands: Commands,
){
    for (entity, mut assets_to_load) in blueprint_assets_to_load.iter_mut(){
        let mut all_loaded = true;
        let mut loaded_amount = 0;
        let total = assets_to_load.asset_infos.len();
        for tracker in assets_to_load.asset_infos.iter_mut(){
            let asset_id = tracker.id;
            let loaded = asset_server.is_loaded_with_dependencies(asset_id);
            tracker.loaded = loaded;
            if loaded {
                loaded_amount += 1;
            }else{
                all_loaded = false;
            }
        }
        let progress:f32 = loaded_amount as f32 / total as f32;
        println!("progress: {}",progress);
        assets_to_load.progress = progress;

        if all_loaded {
            assets_to_load.all_loaded = true;
            commands.entity(entity)
                .insert(BlueprintAssetsLoaded)
                .remove::<BlueprintAssetsNotLoaded>();
        }
    }
}

pub(crate) fn actually_spawn_stuff(
    spawn_placeholders: Query<
    (
        Entity,
        &BlueprintName,
        Option<&Transform>,
        Option<&Parent>,
        Option<&Library>,
        Option<&AddToGameWorld>,
        Option<&Name>,
    ),
    (With<BlueprintAssetsLoaded>, Added<BlueprintAssetsLoaded>, Without<BlueprintAssetsNotLoaded>),
    >,

    mut commands: Commands,
    mut game_world: Query<Entity, With<GameWorldTag>>,

    assets_gltf: Res<Assets<Gltf>>,
    asset_server: Res<AssetServer>,
    blueprints_config: Res<BluePrintsConfig>,

    children: Query<&Children>,
){

    for (
        entity,
        blupeprint_name,
        transform,
        original_parent,
        library_override,
        add_to_world,
        name,

    ) in spawn_placeholders.iter()
    {
        info!(
            "need to spawn {:?} for entity {:?}, id: {:?}, parent:{:?}",
            blupeprint_name.0, name, entity, original_parent
        );

        let what = &blupeprint_name.0;
        let model_file_name = format!("{}.{}", &what, &blueprints_config.format);

        // library path is either defined at the plugin level or overriden by optional Library components
        let library_path =
            library_override.map_or_else(|| &blueprints_config.library_folder, |l| &l.0);
        let model_path = Path::new(&library_path).join(Path::new(model_file_name.as_str()));

        info!("attempting to spawn {:?}", model_path);
        let model_handle: Handle<Gltf> = asset_server.load(model_path);// FIXME: kinda weird now 

        let gltf = assets_gltf
            .get(&model_handle)
            .expect("this gltf should have been loaded");

        // WARNING we work under the assumtion that there is ONLY ONE named scene, and that the first one is the right one
        let main_scene_name = gltf
            .named_scenes
            .keys()
            .next()
            .expect("there should be at least one named scene in the gltf file to spawn");

        let scene = &gltf.named_scenes[main_scene_name];

        // transforms are optional, but still deal with them correctly
        let mut transforms: Transform = Transform::default();
        if transform.is_some() {
            transforms = *transform.unwrap();
        }

        let mut original_children: Vec<Entity> = vec![];
        if let Ok(c) = children.get(entity) {
            for child in c.iter() {
                original_children.push(*child);
            }
        }
        commands.entity(entity).insert((
            SceneBundle {
                scene: scene.clone(),
                transform: transforms,
                ..Default::default()
            },
            Animations {
                named_animations: gltf.named_animations.clone(),
            },
            Spawned,
            OriginalChildren(original_children),
        ));

        if add_to_world.is_some() {
            let world = game_world
                .get_single_mut()
                .expect("there should be a game world present");
            commands.entity(world).add_child(entity);
        }
    }
}