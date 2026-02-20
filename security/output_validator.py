def validate_output_schema(payload: dict, required: list[str]) -> bool:
    return all(k in payload for k in required)
