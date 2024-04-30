use bevy::log::{debug, warn};
use bevy::reflect::serde::UntypedReflectDeserializer;
use bevy::reflect::{Reflect, TypeRegistration, TypeRegistry};
use bevy::utils::HashMap;
use ron::Value;
use serde::de::DeserializeSeed;

use super::capitalize_first_letter;

pub fn ronstring_to_reflect_component(
    ron_string: &str,
    type_registry: &TypeRegistry,
) -> Vec<(Box<dyn Reflect>, TypeRegistration)> {
    let lookup: HashMap<String, Value> = ron::from_str(ron_string).unwrap();
    let mut components: Vec<(Box<dyn Reflect>, TypeRegistration)> = Vec::new();
    for (key, value) in lookup.into_iter() {
        let type_string = key.replace("component: ", "").trim().to_string();
        let capitalized_type_name = capitalize_first_letter(type_string.as_str());

        let parsed_value: String;
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
            let reflect_deserializer = UntypedReflectDeserializer::new(type_registry);
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
