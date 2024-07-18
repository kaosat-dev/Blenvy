use bevy::log::{debug, warn};
use bevy::reflect::serde::ReflectDeserializer;
use bevy::reflect::{Reflect, TypeInfo, TypeRegistration, TypeRegistry};
use bevy::utils::HashMap;
use ron::Value;
use serde::de::DeserializeSeed;

use super::capitalize_first_letter;

pub fn ronstring_to_reflect_component(
    ron_string: &str,
    type_registry: &TypeRegistry,
    simplified_types: bool,
) -> Vec<(Box<dyn Reflect>, TypeRegistration)> {
    let lookup: HashMap<String, Value> = ron::from_str(ron_string).unwrap();
    let mut components: Vec<(Box<dyn Reflect>, TypeRegistration)> = Vec::new();
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
            if simplified_types {
                if let TypeInfo::TupleStruct(info) = type_registration.type_info() {
                    // we handle tupple strucs with only one field differently, as Blender's custom properties with custom ui (float, int, bool, etc) always give us a tupple struct
                    if info.field_len() == 1 {
                        let field = info
                            .field_at(0)
                            .expect("we should always have at least one field here");
                        let field_name = field.type_path();
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

                if parsed_value.is_empty() {
                    parsed_value = "()".to_string();
                }
            }
            let ron_string = format!(
                "{{ \"{}\":{} }}",
                type_registration.type_info().type_path(),
                parsed_value
            );

            // usefull to determine what an entity looks like Serialized
            /*let test_struct = CameraRenderGraph::new("name");
            let serializer = ReflectSerializer::new(&test_struct, &type_registry);
            let serialized =
                ron::ser::to_string_pretty(&serializer, ron::ser::PrettyConfig::default()).unwrap();
            println!("serialized Component {}", serialized);*/

            debug!("component data ron string {}", ron_string);
            let mut deserializer = ron::Deserializer::from_str(ron_string.as_str())
                .expect("deserialzer should have been generated from string");
            let reflect_deserializer = ReflectDeserializer::new(type_registry);
            let component = reflect_deserializer
                .deserialize(&mut deserializer)
                .unwrap_or_else(|_| {
                    panic!(
                        "failed to deserialize component {} with value: {:?}",
                        key, value
                    )
                });

            debug!("component {:?}", component);
            debug!("real type {:?}", component.get_represented_type_info());
            components.push((component, type_registration.clone()));
            debug!("found type registration for {}", capitalized_type_name);
        } else {
            warn!("no type registration for {}", capitalized_type_name);
        }
    }
    components
}
