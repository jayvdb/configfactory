from collections import OrderedDict

from django.test import TestCase

from configfactory.utils import dicthelper


class DictHelperTestCase(TestCase):

    def test_flatten_dict(self):

        actual = dicthelper.flatten(OrderedDict([
            ('a', OrderedDict([
                ('b', OrderedDict([
                    ('c', 'one')
                ])),
                ('d', 'two')
            ])),
            ('e', 'three')
        ]))

        assert actual == OrderedDict([
            ('a.b.c', 'one'),
            ('a.d', 'two'),
            ('e', 'three')
        ])

    def test_merge_dicts(self):

        actual = dicthelper.merge(
            OrderedDict([
                ('a', 'one'),
                ('b', OrderedDict([
                    ('c', 'two'),
                    ('d', OrderedDict([
                        ('e', 'three'),
                    ])),
                    ('f', 'four')
                ])),
                ('i', 'six'),
            ]),
            OrderedDict([
                ('a', 'one - merged'),
                ('b', OrderedDict([
                    ('c', 'two - merged'),
                    ('d', OrderedDict([
                        ('e', 'three - merged'),
                        ('g', 'five'),
                    ])),
                    ('f', 'four')
                ])),
                ('h', 'seven'),
            ]),
        )

        assert actual == OrderedDict([
            ('a', 'one - merged'),
            ('b', OrderedDict([
                ('c', 'two - merged'),
                ('d', OrderedDict([
                    ('e', 'three - merged'),
                    ('g', 'five')
                ])),
                ('f', 'four')
            ])),
            ('i', 'six'),
            ('h', 'seven'),
        ])

    def test_merge_dict_with_lists(self):

        actual = dicthelper.merge({
            'key1': [
                {
                    'id': 1,
                    'name': ''
                }
            ]
        }, {
            'key1': [
                {
                    'id': 1,
                    'name': 'Test'
                }
            ]
        })

        assert actual == {
            'key1': [
                {
                    'id': 1,
                    'name': 'Test'
                }
            ]
        }

    def test_traverse_dict_without_callback(self):

        actual = dicthelper.traverse(OrderedDict([
            ('a', 'one'),
            ('b', OrderedDict([
                ('c', OrderedDict([
                    ('d', 'two'),
                    ('e', 'three')
                ])),
                ('f', 'four')
            ])),
            ('g', 'five')
        ]))

        assert actual == OrderedDict([
            ('a', 'one'),
            ('b', OrderedDict([
                ('c', OrderedDict([
                    ('d', 'two'),
                    ('e', 'three')
                ])),
                ('f', 'four')
            ])),
            ('g', 'five')
        ])

    def test_traverse_dict_upper_callback(self):

        actual = dicthelper.traverse(OrderedDict([
            ('a', 'one'),
            ('b', OrderedDict([
                ('c', OrderedDict([
                    ('d', 'two'),
                    ('e', 'three')
                ])),
                ('f', 'four')
            ])),
            ('g', 'five'),
            ('h', ['six', OrderedDict([
                ('i', 'seven'),
                ('j', 'eight')
            ])])
        ]), lambda v, p: v.upper())

        assert actual == OrderedDict([
            ('a', 'ONE'),
            ('b', OrderedDict([
                ('c', OrderedDict([
                    ('d', 'TWO'),
                    ('e', 'THREE')
                ])),
                ('f', 'FOUR')
            ])),
            ('g', 'FIVE'),
            ('h', ['SIX', OrderedDict([
                ('i', 'SEVEN'),
                ('j', 'EIGHT')
            ])])
        ])
