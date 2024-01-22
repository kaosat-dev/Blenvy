   """elif ref_name not in type_infos and ref_name.startswith("alloc::vec::Vec<"):
            #TODO: CLEANUP, this is essentially the same as above
            ref_name = ref_name.replace("alloc::vec::Vec<", "").replace(">", "")
            short_name = ref_name.split(":")[-1]
            print("new ref", ref_name, "short_name", short_name)
            original = {
                "isComponent": False,
                "isResource": False,
                "items": {
                    "type": {
                    "$ref": "#/$defs/" + ref_name
                    }
                },
                "short_name": "Vec<"+short_name+">",
                "title": ref_name,
                "type": "array",
                "typeInfo": "List"
            }
            print("FAKE ORIGINAL TYPE", original)
            original_type_name = original["title"]

            is_value_type = original_type_name in value_types_defaults

            value = value_types_defaults[original_type_name] if is_value_type else None
            default_values.append(value)
            prefix_infos.append(original)


            if is_value_type:
                if original_type_name in blender_property_mapping:
                    blender_property_def = blender_property_mapping[original_type_name]

                    print("HERE", short_name, original)
                    blender_property = blender_property_def["type"](
                        **blender_property_def["presets"],# we inject presets first
                        name = property_name, 
                        default=value,
                        update= update_calback_helper(definition, update, component_name_override)
                    )
                  
                    __annotations__[property_name] = blender_property
            else:
                print("NESTING")
                print("NOT A VALUE TYPE", original)
                original_long_name = original["title"]
                (sub_component_group, _) = process_component(registry, original, update, {"nested": True, "type_name": original_long_name}, component_name_override=short_name)
                # TODO: use lookup in registry, add it if necessary, or retrieve it if it already exists
                __annotations__[property_name] = sub_component_group"""
