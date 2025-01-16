from typing import Any, Dict
from copy import deepcopy

GPT_BASE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "my_schema",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {},
        },
    },
}


def build_json_schema(
    property_schema_map: Dict[str, Dict[str, Any]], json_schema_name: str = None
) -> Dict[str, Any]:

    def enforce_no_extra_properties(schema):
        # Ensure that original schema is not modified
        schema = deepcopy(schema)

        if isinstance(schema, dict):
            if schema.get("type") == "object":
                schema["additionalProperties"] = False
            for value in schema.values():
                enforce_no_extra_properties(value)
        elif isinstance(schema, list):
            for item in schema:
                enforce_no_extra_properties(item)
        return schema

    # Create a deep copy of the base schema to avoid modifications
    final_schema = deepcopy(GPT_BASE_SCHEMA)

    if json_schema_name is not None:
        final_schema["json_schema"]["name"] = json_schema_name

    # Deep copy each schema in the input map to avoid modifying originals
    for property_name, schema in deepcopy(property_schema_map).items():
        final_schema["json_schema"]["schema"]["properties"][property_name] = schema

    # Add all keys from the property schema map to the 'required' list
    final_schema["json_schema"]["schema"]["required"] = list(property_schema_map.keys())

    # Apply additionalProperties: False to ensure immutability
    final_schema = enforce_no_extra_properties(final_schema)

    return final_schema
