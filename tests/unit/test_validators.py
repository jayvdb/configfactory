import pytest
from django.core.exceptions import ValidationError

from configfactory.validators import validate_settings_format


def test_validate_settings_object_type():

    validate_settings_format({})


def test_validate_settings_object_property_types():

    validate_settings_format({
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

    with pytest.raises(ValidationError) as exc_info:
        validate_settings_format({
            'list': [
                {
                    'a': 1
                },
                {
                    'b': 2
                }
            ],
        })

    exc: ValidationError = exc_info.value

    assert exc.message == 'Invalid settings format.'
