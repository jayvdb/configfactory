import pytest

from configfactory.utils import jsonschema


def test_validate_settings_object_type():
    jsonschema.validate_settings({})


def test_validate_settings_object_property_types():
    jsonschema.validate_settings({
        'string': 'string',
        'number': 1.5,
        'boolean': True,
        'integer': 10,
        'null': None,
        'list': [1, 2, 3],
        'inner': {
            'string': 'string',
            'number': 1.5,
            'boolean': True,
            'integer': 10,
            'null': None,
            'list': [1, 2, 3],
        }
    })


def test_validate_settings_invalid_list_property():
    with pytest.raises(jsonschema.JSONSchemaError):
        jsonschema.validate_settings({
            'list': [
                {
                    'a': 1
                },
                {
                    'b': 2
                }
            ],
        })
