

ronstring_to_reflect_component
    => type_registry 
        => type_registration
            => ron_string
        => reflect_deserializer
            => Box<dyn Reflect>
    ==> Box<dyn Reflect>
    

main
    component_targeting
        => Vec<Box<dyn Reflect>>
            ==> hashmap
    component upsert
        => hashmap
        => type_registry 
        => type_registration

# possible issues: 
    * the lack of origin SCENE might cause issues, as up until now, data was per SCENE
    * we cannot trace any data back to its gltf file of origin, though that might be best suited to be at the blueprints
        level, although