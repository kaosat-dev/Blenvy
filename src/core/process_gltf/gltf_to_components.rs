use std::collections::HashMap;
use core::ops::Deref;

use serde_json::Value;
use serde::de::DeserializeSeed;

use bevy::prelude::*;
use bevy::reflect::serde::{UntypedReflectDeserializer, ReflectSerializer};
use bevy::reflect::TypeRegistryInternal;
use bevy::gltf::{Gltf, GltfExtras};

use super::capitalize_first_letter;

pub fn gltf_extras_to_components(
    gltf: &mut Gltf,
    scenes: &mut ResMut<Assets<Scene>>,
    type_registry: impl Deref<Target = TypeRegistryInternal>,
    gltf_name: &str
){
    let mut added_components = 0;  
    for (_name, scene) in &gltf.named_scenes {
      info!("gltf: {:?} scene name {:?}", gltf_name, _name);
   
      let scene = scenes.get_mut(scene).unwrap();

      let mut query = scene.world.query::<(Entity, &Name, &GltfExtras, &Parent)>();
      let mut entity_components: HashMap<Entity, Vec<Box<dyn Reflect>> > = HashMap::new();
      for (entity, name, extras, parent) in query.iter(&scene.world) {
        debug!("Name: {}, entity {:?}, parent: {:?}", name, entity, parent);
        let reflect_components = ronstring_to_reflect_component(&extras.value, &type_registry);
        added_components = reflect_components.len();
        debug!("Found components {}", added_components);

        // we assign the components specified in entity_data/xxx_components objects to their parent node
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
          
        
        }else {
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

      // println!("FOUND ASSET {:?}", foob);
      // GltfNode
      // find a way to link this name to the current entity ? => WOULD BE VERY USEFULL for animations & co !!
      debug!("done pre-processing components, now adding them to entities");
      for (entity, components) in entity_components {
        if components.len() > 0 {
          debug!("--entity {:?}, components {}", entity, components.len());
        }
        for component in components {
            let mut entity_mut = scene.world.entity_mut(entity);
            debug!("------adding {} {:?}", component.type_name(), component);

            type_registry
                .get_with_name(component.type_name())
                .unwrap() // Component was successfully deserialized, it has to be in the registry
                .data::<ReflectComponent>()
                .unwrap() // Hopefully, the component deserializer ensures those are components
                .insert(&mut entity_mut, &*component)
                ; 

            // info!("all components {:?}", scene.world.entity(entity).archetype().components());
            // scene.world.components().
                // TODO: how can we insert any additional components "by hand" here ?
        }
        let e_mut = scene.world.entity_mut(entity);
        let archetype = e_mut.archetype().clone();//.components();
        let _all_components = archetype.components();
        // println!("All components {:?}", all_components);

        if added_components > 0 {
          debug!("------done adding {} components", added_components);
        }
      }
    }
    info!("done extracting gltf_extras /n");   
  }
  

  pub fn ronstring_to_reflect_component(
    ron_string: &String,
    type_registry: &TypeRegistryInternal
  ) -> Vec<Box<dyn Reflect>> {
    let lookup: HashMap<String, Value> = ron::from_str(ron_string.as_str()).unwrap(); 
    let mut components: Vec<Box<dyn Reflect>> = Vec::new();
    for (key, value) in lookup.into_iter() {
      let type_string = key.replace("component: ", "").trim().to_string();
      let capitalized_type_name = capitalize_first_letter(type_string.as_str());
      // println!("capitalized_type_name {}", capitalized_type_name);

      let mut parsed_value = format!("{}", value);
      parsed_value = ron::from_str(parsed_value.as_str()).unwrap_or(parsed_value);
  
      if let Some(type_registration) = type_registry.get_with_short_name(capitalized_type_name.as_str()) {  
        // FIXME : in the long run, replace all the text based, clunky unoptimised things with use of type_registration.type_info()
        let blabla = type_registry.get_with_name("bevy_render::color::Color").unwrap();
        println!("TYPE INFO {:?}", type_registration.type_info());
        // println!("parsed value {}",parsed_value);       
        if parsed_value == "" {
          parsed_value = "()".to_string();
        } 
        else if parsed_value.starts_with("[") && parsed_value.ends_with("]")  {
          // FIXME/ horrible, and how about actual vec!s and not vec2/vec3 s? 
          // the worst part is, we have the component information, so we SHOULD be able to infer the input struct type
          // perhaps use better logic than the unwrap ? we could do parsed:Vec<u64> as well, and drop it otherwise ?
          let parsed: Vec<f32> = ron::from_str(&parsed_value).unwrap();
          if parsed.len() == 2 {
            parsed_value = format!("((x:{},y:{}))", parsed[0], parsed[1]);
          }
          // FIXME god awfull hacks
          if parsed.len() == 3 && !key.to_lowercase().contains("color"){          
            parsed_value = format!("((x:{},y:{},z:{}))", parsed[0], parsed[1], parsed[2]);
          }
          if parsed.len() == 3 && key.to_lowercase().contains("color"){          
            parsed_value = format!("(Rgba(red:{},green:{},blue:{}, alpha: 1.0))", parsed[0], parsed[1], parsed[2]);
          }
          if parsed.len() == 4 && !key.to_lowercase().contains("color") {          
            parsed_value = format!("((x:{},y:{},z:{},w:{}))", parsed[0], parsed[1], parsed[2], parsed[3]);
          }
          if parsed.len() == 4 && key.to_lowercase().contains("color"){          
            parsed_value = format!("(Rgba(red:{},green:{},blue:{}, alpha:{}))", parsed[0], parsed[1], parsed[2], parsed[3]);
          }
          /*match ron::from_str(&parsed_value) {
            Err(e) => panic!("{:?}", e),
            Ok::<Vec<f32>, _>(parsed) => {
              if parsed.len() == 2 {
                parsed_value = format!("((x:{},y:{}))", parsed[0], parsed[1]);
              }
              if parsed.len() == 3 {          
                parsed_value = format!("((x:{},y:{},z:{}))", parsed[0], parsed[1], parsed[2]);
              }
            },
            Ok::<Color, _>(parsed) => {
              parsed_value = format!("((x:{},y:{}))", parsed[0], parsed[1]);
            }
          }*/
         
        }
        // FIXME: inneficient
        else if parsed_value.starts_with("\"") && parsed_value.ends_with("\"") {
            parsed_value = format!("({})",parsed_value);
        }
        else {
          // FIXME: inneficient
          if let Ok(parsed) =  parsed_value.parse::<f32>() {
            parsed_value = format!("({})",parsed);
          }
          else if let Ok(parsed) =  parsed_value.parse::<f64>() {
            parsed_value = format!("({})",parsed);
          }
          else if let Ok(parsed) =  parsed_value.parse::<u64>() {
            parsed_value = format!("({})",parsed);
          }
          else if let Ok(parsed) =  parsed_value.parse::<bool>() {
            parsed_value = format!("({})",parsed);
          }
        }
      
        let ron_string = format!("{{ \"{}\":{} }}",
          type_registration.type_name(),
          parsed_value
        );

         
        // usefull to determine what an entity looks like Serialized
        /*let test_struct = TuppleTestStr::default();
        let serializer = ReflectSerializer::new(&test_struct, &type_registry);
        let serialized =
            ron::ser::to_string_pretty(&serializer, ron::ser::PrettyConfig::default()).unwrap();
        println!("serialized Component {}", serialized);*/

        debug!("component data ron string {}", ron_string);
        let mut deserializer =  ron::Deserializer::from_str(ron_string.as_str()).unwrap();
        let reflect_deserializer = UntypedReflectDeserializer::new(&type_registry);
        let component = reflect_deserializer.deserialize(&mut deserializer).expect(format!("failed to deserialize component {} with value: {}", key, value).as_str());

        components.push(component);
        debug!("found type registration for {}", capitalized_type_name);
      } else {
        warn!("no type registration for {}", capitalized_type_name);
      }
    }
    components
  }
  
