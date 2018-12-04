import jsonschema
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

SETTINGS_JSONSCHEMA = {
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


def validate_settings_format(value: dict):
    try:
        jsonschema.validate(value, schema=SETTINGS_JSONSCHEMA)
    except (jsonschema.ValidationError, jsonschema.SchemaError):
        raise ValidationError(_('Invalid settings format.'))
