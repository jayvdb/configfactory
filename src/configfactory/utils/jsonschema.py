import jsonschema

SETTINGS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "$ref": "#/definitions/settings",
    "definitions": {
        "settings": {
            "type": "object",
            "patternProperties": {
                "^.*$": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "number"},
                        {"type": "boolean"},
                        {"type": "integer"},
                        {"type": "null"},
                        {
                            "type": "array",
                            "items": {
                                "type": [
                                    "string",
                                    "number",
                                    "boolean",
                                    "integer",
                                    "null"
                                ]
                            }
                        },
                        {
                            "type": "object",
                            "$ref": "#/definitions/settings"
                        }
                    ]
                }
            },
            "additionalProperties": False
        }
    }
}


class JSONSchemaError(Exception):
    def __init__(self, message: str):
        self.message = message


def validate(instance, schema: dict):
    try:
        jsonschema.validate(instance, schema=schema)
    except (jsonschema.ValidationError, jsonschema.SchemaError) as exc:
        raise JSONSchemaError(exc.message)


def validate_settings(instance: dict):
    validate(instance, schema=SETTINGS_SCHEMA)
