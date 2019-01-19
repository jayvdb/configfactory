from configfactory.utils import dictutil


def test_merge_dicts():

    actual = dictutil.merge(
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

    actual = dictutil.merge(
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


def test_flatten_dict():

    actual = dictutil.flatten({
        'a': {
            'b': {
                'c': {
                    'd': 'e'
                }
            }
        },
        'f': 1,
        'g': [1, 2, 3],
        'h': {
            'i': 1,
            'j': 2
        }
    })

    assert actual == {
        'a.b.c.d': 'e',
        'f': 1,
        'g': [1, 2, 3],
        'h.i': 1,
        'h.j': 2,
    }
