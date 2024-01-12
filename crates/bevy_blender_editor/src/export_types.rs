use std::{io::Write, fs::File};

use bevy::{scene::DynamicSceneBuilder, utils::HashMap};
use bevy_app::App;
use bevy_ecs::{reflect::{AppTypeRegistry, ReflectComponent, ReflectResource}, world::World};
use bevy_reflect::{TypeInfo, TypePath, TypeRegistration, VariantInfo};
use serde_json::{json, Map, Value};

use crate::ExportComponentsConfig;


pub fn export_types(world: &mut World) {
    println!("EXPOOOORT");
    let mut writer = File::create("schema.json").expect("should have created schema file");

    let config = world
        .get_resource::<ExportComponentsConfig>()
        .expect("ExportComponentsConfig should exist at this stage");

    let filter = config
        .component_filter
        .clone();
    let filter_resources = config
        .resource_filter
        .clone();

    let scene_builder = DynamicSceneBuilder::from_world(&world)
        .with_filter(filter.clone())
        .with_resource_filter(filter_resources.clone());
    
    let foo = scene_builder
    // .extract_entities(vec![])
    .extract_resources()
    .build();
    // foo.write_to_world(world, entity_map)
    println!("EXPOOOORT 2");

    let mut filtered_world = World::new();
    filtered_world.init_resource::<AppTypeRegistry>();
    foo.write_to_world(&mut filtered_world, &mut HashMap::default()).expect("writing to filtered world should have worked");

    let mut target_world = filtered_world; // self.world

    let types = world.resource_mut::<AppTypeRegistry>();

    let types = types.read();
    let mut schemas = types.iter().map(export_type).collect::<Map<_, _>>();

    serde_json::to_writer_pretty(
        writer,
        &json!({
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "bevy game schema",
            "$defs": schemas,
        }),
    )
    .expect("valid json");

    println!("DONE")
}

pub trait ExportTypesExt {
    fn export_types(&mut self, writer: impl Write);
}

impl ExportTypesExt for App {
    fn export_types(&mut self, writer: impl Write) {


        let config = self.world
            .get_resource::<ExportComponentsConfig>()
            .expect("ExportComponentsConfig should exist at this stage");

        let filter = config
            .component_filter
            .clone();
        let filter_resources = config
            .resource_filter
            .clone();

        let scene_builder = DynamicSceneBuilder::from_world(&self.world)
            .with_filter(filter.clone())
            .with_resource_filter(filter_resources.clone());
        let foo = scene_builder.build();
        // foo.write_to_world(world, entity_map)

        let mut filtered_world = World::new();
        foo.write_to_world(&mut filtered_world, &mut HashMap::default()).expect("writing to filtered world should have worked");

        let mut target_world = filtered_world; // self.world

        let types = self.world.resource_mut::<AppTypeRegistry>();

        let types = types.read();
        let mut schemas = types.iter().map(export_type).collect::<Map<_, _>>();

        serde_json::to_writer_pretty(
            writer,
            &json!({
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": "bevy game schema",
                "$defs": schemas,
            }),
        )
        .expect("valid json");

        eprintln!("wrote schema containing {} types", schemas.len());
    }
}

pub fn export_type(reg: &TypeRegistration) -> (String, Value) {
    let t = reg.type_info();
    let mut schema = match t {
        TypeInfo::Struct(info) => {
            let properties = info
                .iter()
                .enumerate()
                .map(|(idx, field)| {
                    (
                        field.name().to_owned(),
                        add_min_max(json!({ "type": typ(field.type_path()) }), reg, idx, None),
                    )
                })
                .collect::<Map<_, _>>();

            json!({
                "type": "object",
                "typeInfo": "Struct",
                "title": t.type_path(),
                "properties": properties,
                "additionalProperties": false,
                "required": info
                    .iter()
                    .filter(|field| !field.type_path().starts_with("core::option::Option"))
                    .map(|field| field.name())
                    .collect::<Vec<_>>(),
            })
        }
        TypeInfo::Enum(info) => {
            let simple = info
                .iter()
                .all(|variant| matches!(variant, VariantInfo::Unit(_)));
            if simple {
                json!({
                    "type": "string",
                    "typeInfo": "Enum",
                    "title": t.type_path(),
                    "enum": info
                        .iter()
                        .map(|variant| match variant {
                            VariantInfo::Unit(v) => v.name(),
                            _ => unreachable!(),
                        })
                        .collect::<Vec<_>>(),
                })
            } else {
                let variants = info
                .iter()
                .enumerate()
                .map(|(field_idx, variant)| match variant {
                    VariantInfo::Struct(v) => json!({
                        "type": "object",
                        "title": t.type_path(),
                        "properties": v
                            .iter()
                            .enumerate()
                            .map(|(variant_idx, field)| (field.name().to_owned(), add_min_max(json!({"type": typ(field.type_path()), "title": field.name()}), reg, field_idx, Some(variant_idx))))
                            .collect::<Map<_, _>>(),
                        "additionalProperties": false,
                        "required": v
                            .iter()
                            .filter(|field| !field.type_path().starts_with("core::option::Option"))
                            .map(|field| field.name())
                            .collect::<Vec<_>>(),
                    }),
                    VariantInfo::Tuple(v) => json!({
                        "type": "array",
                        "prefixItems": v
                            .iter()
                            .enumerate()
                            .map(|(variant_idx, field)| add_min_max(json!({"type": typ(field.type_path())}), reg, field_idx, Some(variant_idx)))
                            .collect::<Vec<_>>(),
                        "items": false,
                    }),
                    VariantInfo::Unit(v) => json!({
                        "const": v.name(),
                    }),
                })
                .collect::<Vec<_>>();

                json!({
                    "type": "object",
                    "typeInfo": "Enum",
                    "title": t.type_path(),
                    "oneOf": variants,
                })
            }
        }
        TypeInfo::TupleStruct(info) => json!({
            "title": t.type_path(),
            "type": "array",
            "typeInfo": "TupleStruct",
            "prefixItems": info
                .iter()
                .enumerate()
                .map(|(idx, field)| add_min_max(json!({"type": typ(field.type_path())}), reg, idx, None))
                .collect::<Vec<_>>(),
            "items": false,
        }),
        TypeInfo::List(info) => {
            json!({
                "title": t.type_path(),
                "type": "array",
                "typeInfo": "List",
                "items": json!({"type": typ(info.item_type_path_table().path())}),
            })
        }
        TypeInfo::Array(info) => json!({
            "title": t.type_path(),
            "type": "array",
            "typeInfo": "Array",
            "items": json!({"type": typ(info.item_type_path_table().path())}),
        }),
        TypeInfo::Map(info) => json!({
            "title": t.type_path(),
            "type": "object",
            "typeInfo": "Map",
            "additionalProperties": json!({"type": typ(info.value_type_path_table().path())}),
        }),
        TypeInfo::Tuple(info) => json!({
            "title": t.type_path(),
            "type": "array",
            "typeInfo": "Tuple",
            "prefixItems": info
                .iter()
                .enumerate()
                .map(|(idx, field)| add_min_max(json!({"type": typ(field.type_path())}), reg, idx, None))
                .collect::<Vec<_>>(),
            "items": false,
        }),
        TypeInfo::Value(info) => json!({
            "title": t.type_path(),
            "type": map_json_type(info.type_path()),
            "typeInfo": "Value",
        }),
    };
    schema.as_object_mut().unwrap().insert(
        "isComponent".to_owned(),
        reg.data::<ReflectComponent>().is_some().into(),
    );
    schema.as_object_mut().unwrap().insert(
        "isResource".to_owned(),
        reg.data::<ReflectResource>().is_some().into(),
    );
    (t.type_path().to_owned(), schema)
}

fn typ(t: &str) -> Value {
    json!({ "$ref": format!("#/$defs/{t}") })
}

fn map_json_type(t: &str) -> Value {
    match t {
        "bool" => "boolean",
        "u8" | "u16" | "u32" | "u64" | "u128" | "usize" => "uint",
        "i8" | "i16" | "i32" | "i64" | "i128" | "isize" => "int",
        "f32" | "f64" => "float",
        "char" | "str" | "alloc::string::String" => "string",
        _ => "object",
    }
    .into()
}

fn add_min_max(
    mut val: Value,
    reg: &TypeRegistration,
    field_index: usize,
    variant_index: Option<usize>,
) -> Value {
    #[cfg(feature = "support-inspector")]
    fn get_min_max(
        reg: &TypeRegistration,
        field_index: usize,
        variant_index: Option<usize>,
    ) -> Option<(Option<f32>, Option<f32>)> {
        use bevy_inspector_egui::inspector_options::{
            std_options::NumberOptions, ReflectInspectorOptions, Target,
        };

        reg.data::<ReflectInspectorOptions>()
            .and_then(|ReflectInspectorOptions(o)| {
                o.get(if let Some(variant_index) = variant_index {
                    Target::VariantField {
                        variant_index,
                        field_index,
                    }
                } else {
                    Target::Field(field_index)
                })
            })
            .and_then(|o| o.downcast_ref::<NumberOptions<f32>>())
            .map(|num| (num.min, num.max))
    }

    #[cfg(not(feature = "support-inspector"))]
    fn get_min_max(
        _reg: &TypeRegistration,
        _field_index: usize,
        _variant_index: Option<usize>,
    ) -> Option<(Option<f32>, Option<f32>)> {
        None
    }

    let Some((min, max)) = get_min_max(reg, field_index, variant_index) else {
        return val;
    };
    let obj = val.as_object_mut().unwrap();
    if let Some(min) = min {
        obj.insert("minimum".to_owned(), min.into());
    }
    if let Some(max) = max {
        obj.insert("maximum".to_owned(), max.into());
    }
    val
}