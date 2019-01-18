from configfactory.utils import itertool


def test_traverse_upper():

    actual = itertool.traverse({
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
