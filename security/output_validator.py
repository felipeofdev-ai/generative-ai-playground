from jsonschema import Draft202012Validator


def validate_output_schema(payload: dict, required: list[str]) -> bool:
    return all(k in payload for k in required)


def validate_with_json_schema(payload: dict, schema: dict) -> tuple[bool, list[str]]:
    validator = Draft202012Validator(schema)
    errors = [e.message for e in validator.iter_errors(payload)]
    return (len(errors) == 0, errors)
