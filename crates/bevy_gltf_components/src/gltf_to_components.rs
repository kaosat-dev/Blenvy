use core::ops::Deref;

use ron::Value;
use serde::de::DeserializeSeed;

use bevy::ecs::{entity::Entity, reflect::ReflectComponent};
use bevy::gltf::{Gltf, GltfExtras};
use bevy::reflect::serde::UntypedReflectDeserializer; // ReflectSerializer
use bevy::reflect::{Reflect, TypeInfo, TypeRegistry};
use bevy::scene::Scene;
use bevy::utils::HashMap;
use bevy::{
    log::{debug, info, warn},
    prelude::{Assets, Name, Parent, ResMut},
};

use super::capitalize_first_letter;

pub fn ronstring_to_reflect_component(
    ron_string: &String,
    type_registry: &TypeRegistry,
) -> Vec<Box<dyn Reflect>> {
    let lookup: HashMap<String, Value> = ron::from_str(ron_string.as_str()).unwrap();
    let mut components: Vec<Box<dyn Reflect>> = Vec::new();
    for (key, value) in lookup.into_iter() {
        let type_string = key.replace("component: ", "").trim().to_string();
        let capitalized_type_name = capitalize_first_letter(type_string.as_str());

        let mut parsed_value: String;
        match value.clone() {
            Value::String(str) => {
                parsed_value = str;
            }
            _ => parsed_value = ron::to_string(&value).unwrap().to_string(),
        }

        if let Some(type_registration) =
            type_registry.get_with_short_type_path(capitalized_type_name.as_str())
        {
            debug!("TYPE INFO {:?}", type_registration.type_info());
            match type_registration.type_info() {
                TypeInfo::TupleStruct(info) => {
                    // we handle tupple strucs with only one field differently, as Blender's custom properties with custom ui (float, int, bool, etc) always give us a tupple struct
                    if info.field_len() == 1 {
                        let field = info
                            .field_at(0)
                            .expect("we should always have at least one field here");
                        let field_name = field.type_path();
                        // TODO: find a way to cast with typeId instead of this matching
                        /*match field.type_id(){
                          TypeId::of::<f32>() => {
                            println!("WE HAVE A f32");
                          }
                          }
                          Vec3 => {
                            println!("WE HAVE A VEC3");
                            let bla:Vec3 = ron::from_str(&parsed_value).unwrap();
                            println!("bla {}", bla)
                          }
                          _ =>{}
                        }*/

                        let mut formated = parsed_value.clone();
                        match field_name {
                            "f32" => {
                                formated = parsed_value.parse::<f32>().unwrap().to_string();
                            }
                            "f64" => {
                                formated = parsed_value.parse::<f64>().unwrap().to_string();
                            }
                            "u8" => {
                                formated = parsed_value.parse::<u8>().unwrap().to_string();
                            }
                            "u16" => {
                                formated = parsed_value.parse::<u16>().unwrap().to_string();
                            }
                            "u32" => {
                                formated = parsed_value.parse::<u32>().unwrap().to_string();
                            }
                            "u64" => {
                                formated = parsed_value.parse::<u64>().unwrap().to_string();
                            }
                            "u128" => {
                                formated = parsed_value.parse::<u128>().unwrap().to_string();
                            }
                            "glam::Vec2" => {
                                let parsed: Vec<f32> = ron::from_str(&parsed_value).unwrap();
                                formated = format!("(x:{},y:{})", parsed[0], parsed[1]);
                            }
                            "glam::Vec3" => {
                                let parsed: Vec<f32> = ron::from_str(&parsed_value).unwrap();
                                formated =
                                    format!("(x:{},y:{},z:{})", parsed[0], parsed[1], parsed[2]);
                            }
                            "bevy_render::color::Color" => {
                                let parsed: Vec<f32> = ron::from_str(&parsed_value).unwrap();
                                if parsed.len() == 3 {
                                    formated = format!(
                                        "Rgba(red:{},green:{},blue:{}, alpha: 1.0)",
                                        parsed[0], parsed[1], parsed[2]
                                    );
                                }
                                if parsed.len() == 4 {
                                    formated = format!(
                                        "Rgba(red:{},green:{},blue:{}, alpha:{})",
                                        parsed[0], parsed[1], parsed[2], parsed[3]
                                    );
                                }
                            }
                            _ => {}
                        }

                        parsed_value = format!("({formated})");
                    }
                }
                _ => {}
            }

            // println!("parsed value {}",parsed_value);
            if parsed_value.is_empty() {
                parsed_value = "()".to_string();
            }

            let ron_string = format!(
                "{{ \"{}\":{} }}",
                type_registration.type_info().type_path(),
                parsed_value
            );

            // usefull to determine what an entity looks like Serialized
            /*let test_struct = Enemy::default();
            let serializer = ReflectSerializer::new(&test_struct, &type_registry);
            let serialized =
                ron::ser::to_string_pretty(&serializer, ron::ser::PrettyConfig::default()).unwrap();
            println!("serialized Component {}", serialized);*/

            debug!("component data ron string {}", ron_string);
            let mut deserializer = ron::Deserializer::from_str(ron_string.as_str()).unwrap();
            let reflect_deserializer = UntypedReflectDeserializer::new(type_registry);
            let component = reflect_deserializer.deserialize(&mut deserializer).expect(
                format!(
                    "failed to deserialize component {} with value: {:?}",
                    key, value
                )
                .as_str(),
            );

            debug!("component {:?}", component);
            debug!("real type {:?}", component.get_represented_type_info());

            components.push(component);
            debug!("found type registration for {}", capitalized_type_name);
        } else {
            warn!("no type registration for {}", capitalized_type_name);
        }
    }
    components
}

/// main function: injects components into each entity in gltf files that have gltf_extras, using reflection
pub fn gltf_extras_to_components(
    gltf: &mut Gltf,
    scenes: &mut ResMut<Assets<Scene>>,
    type_registry: impl Deref<Target = TypeRegistry>,
) {
    let mut added_components = 0;
    for (_name, scene) in &gltf.named_scenes {
        debug!("gltf: scene name {:?}", _name);

        let scene = scenes.get_mut(scene).unwrap();

        let mut query = scene.world.query::<(Entity, &Name, &GltfExtras, &Parent)>();
        let mut entity_components: HashMap<Entity, Vec<Box<dyn Reflect>>> = HashMap::new();
        for (entity, name, extras, parent) in query.iter(&scene.world) {
            debug!("Name: {}, entity {:?}, parent: {:?}", name, entity, parent);
            let reflect_components = ronstring_to_reflect_component(&extras.value, &type_registry);
            added_components = reflect_components.len();
            debug!("Found components {}", added_components);

            // we assign the components specified /xxx_components objects to their parent node
            let mut target_entity = entity;
            // if the node contains "components" or ends with "_pa" (ie add to parent), the components will not be added to the entity itself but to its parent
            // this is mostly used for Blender collections
            if name.as_str().contains("components") || name.as_str().ends_with("_pa") {
                debug!("adding components to parent");
                target_entity = parent.get();
            }

            debug!("adding to {:?}", target_entity);

            // if there where already components set to be added to this entity (for example when entity_data was refering to a parent), update the vec of entity_components accordingly
            // this allows for example blender collection to provide basic ecs data & the instances to override/ define their own values
            if entity_components.contains_key(&target_entity) {
                let mut updated_components: Vec<Box<dyn Reflect>> = Vec::new();
                let current_components = &entity_components[&target_entity];
                // first inject the current components
                for component in current_components {
                    updated_components.push(component.clone_value());
                }
                // then inject the new components: this also enables overwrite components set in the collection
                for component in reflect_components {
                    updated_components.push(component.clone_value());
                }
                entity_components.insert(target_entity, updated_components);
            } else {
                entity_components.insert(target_entity, reflect_components);
            }
            // shorthand, did not manage to get it working
            /*  entity_components.insert(
            target_entity,
            if entity_components.contains_key(&target_entity) {
              entity_components[&target_entity].push(reflect_components) } else { reflect_components }
            );*/

            debug!("-----value {:?}", &extras.value);
        }

        // GltfNode
        // find a way to link this name to the current entity ? => WOULD BE VERY USEFULL for animations & co !!
        debug!("done pre-processing components, now adding them to entities");
        for (entity, components) in entity_components {
            if !components.is_empty() {
                debug!("--entity {:?}, components {}", entity, components.len());
            }
            for component in components {
                let mut entity_mut = scene.world.entity_mut(entity);
                debug!(
                    "------adding {} {:?}",
                    component.get_represented_type_info().unwrap().type_path(),
                    component
                );

                let component_type_path =
                    component.get_represented_type_info().unwrap().type_path();
                type_registry
                    .get_with_type_path(component_type_path)
                    .unwrap() // Component was successfully deserialized, it has to be in the registry
                    .data::<ReflectComponent>()
                    .unwrap() // Hopefully, the component deserializer ensures those are components
                    .insert(&mut entity_mut, &*component);

                // debug!("all components {:?}", scene.world.entity(entity).archetype().components());
                // scene.world.components().
                // TODO: how can we insert any additional components "by hand" here ?
            }
            // let entity_mut = scene.world.entity_mut(entity);
            // let archetype = entity_mut.archetype().clone();
            // let _all_components = archetype.components();

            if added_components > 0 {
                debug!("------done adding {} components", added_components);
            }
        }
    }
    info!("done injecting components from gltf_extras /n");
}
