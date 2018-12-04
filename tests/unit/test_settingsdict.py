from configfactory.utils.settingsdict import SettingsDict


def test_create_empty_settingsdict():
    settings = SettingsDict()

    assert not settings


def test_validate_object_type():
    settings = SettingsDict({})

    assert settings.valid


def test_validate_object_property_types():
    settings = SettingsDict({
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

    assert settings.valid


def test_validate_invalid_list_property():
    settings = SettingsDict({
        'list': [
            {
                'a': 1
            },
            {
                'b': 2
            }
        ],
    })

    assert not settings.valid


def test_to_dotenv():
    settings = SettingsDict({
        'a': {
            'b': 10
        },
        'c': True,
        'd': [1, 2, 3]
    })

    assert settings.to_dotenv() == '\n'.join([
        'A_B=10',
        'C=true',
        'D=1,2,3',
    ])
