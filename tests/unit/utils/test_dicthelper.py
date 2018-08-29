from django.test import TestCase

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


def test_traverse_dict_without_callback():

    actual = dicthelper.traverse({
        'a': 'one',
        'b': {
            'c': {
                'd': 'two',
                'e': 'three'
            },
            'f': 'four'
        },
        'g': 'five'
    })

    assert actual == {
        'a': 'one',
        'b': {
            'c': {
                'd': 'two',
                'e': 'three'
            },
            'f': 'four'
        },
        'g': 'five'
    }


def test_traverse_dict_upper_callback():

    actual = dicthelper.traverse({
        'a': 'one',
        'b': {
            'c': {
                'd': 'two',
                'e': 'three'
            },
            'f': 'four'
        },
        'g': 'five',
        'h': [
            'six',
            {
                'i': 'seven',
                'j': 'eight'
            }
        ]
    }, lambda v, p: v.upper())

    assert actual == {
        'a': 'ONE',
        'b': {
            'c': {
                'd': 'TWO',
                'e': 'THREE'
            },
            'f': 'FOUR'
        },
        'g': 'FIVE',
        'h': [
            'SIX',
            {
                'i': 'SEVEN',
                'j': 'EIGHT'
            }
        ]
    }
