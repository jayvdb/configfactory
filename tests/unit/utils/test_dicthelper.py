from configfactory.utils import dicthelper


def test_merge_dicts():

    actual = dicthelper.merge(
        {
            'a': 'one',
            'b': {
                'c': 'two',
                'd': {
                    'e': 'three'
                },
                'f': 'four'
            },
            'i': 'six'
        },
        {
            'a': 'one - merged',
            'b': {
                'c': 'two - merged',
                'd': {
                    'e': 'three - merged',
                    'g': 'five'
                },
                'f': 'four'
            },
            'h': 'seven'
        }
    )

    assert actual == {
        'a': 'one - merged',
        'b': {
            'c': 'two - merged',
            'd': {
                'e': 'three - merged',
                'g': 'five'
            },
            'f': 'four'
        },
        'i': 'six',
        'h': 'seven'
    }


def test_merge_dict_with_lists():

    actual = dicthelper.merge(
        {
            'key1': [
                {
                    'id': 1,
                    'name': ''
                }
            ]
        },
        {
            'key1': [
                {
                    'id': 1,
                    'name': 'Test'
                }
            ]
        }
    )

    assert actual == {
        'key1': [
            {
                'id': 1,
                'name': 'Test'
            }
        ]
    }
