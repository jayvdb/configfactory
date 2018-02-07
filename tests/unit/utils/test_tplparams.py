from django.test import TestCase

from configfactory.exceptions import CircularInjectError, InjectKeyError
from configfactory.utils import tplparams


class TemplateParamsUtilsTestCase(TestCase):

    maxDiff = None

    def test_inject_string_data(self):

        data = "a = ${param:a}"

        actual = tplparams.inject(data, params={
            'a': 'TEST'
        })

        self.assertEqual(actual, "a = TEST")

    def test_inject_missing_param_raise_exception(self):

        data = "a = ${param:a}"

        with self.assertRaises(InjectKeyError):
            tplparams.inject(data, params={
                'b': 'TEST'
            }, strict=True)

    def test_inject_missing_param_ignore_exception(self):

        data = "a = ${param:a}"

        actual = tplparams.inject(data, params={
            'b': 'TEST'
        }, strict=False)

        self.assertEqual(actual, 'a = ${param:a}')

    def test_inject_keep_data_type(self):

        data = "${param:a}"

        actual = tplparams.inject(data, params={
            'a': 100
        })

        self.assertEqual(actual, 100)

    def test_inject_non_string(self):

        data = 100

        actual = tplparams.inject(data, params={
            'a': 000
        })

        self.assertEqual(actual, 100)

    def test_inject_params(self):

        data = (
            "a.b.c = ${param:a.b.c}, "
            "b.c = ${param:b.c}, "
            "c.d.e = ${param:c.d.e}"
        )

        self.assertEqual(
            tplparams.inject(data, params={
                'a.b.c': 'ABC',
                'b.c': '${param:a.b.c}:BC',
                'c.d': 'CD',
                'c.d.e': '${param:b.c}:${param:c.d}',
            }),
            "a.b.c = ABC, b.c = ABC:BC, c.d.e = ABC:BC:CD"
        )

    def test_inject_params_to_self_component(self):

        data = (
            "db.host = ${param:db.host}, "
            "db.default.host = ${param:db.host}"
        )

        self.assertEqual(
            tplparams.inject(data, params={
                'db.host': 'localhost',
                'db.default.host': '${param:db.host}',
            }),
            "db.host = localhost, db.default.host = localhost"
        )

    def test_inject_params_to_each_other(self):

        data = (
            "a.a = ${param:a.a}, "
            "a.b = ${param:a.b}, "
            "b.a = ${param:b.a}, "
            "b.b = ${param:b.b}"
        )

        self.assertEqual(
            tplparams.inject(data, params={
                'a.a': 'AA',
                'a.b': '${param:b.b}',
                'b.a': '${param:a.b}',
                'b.b': 'BB',
            }),
            'a.a = AA, a.b = BB, b.a = BB, b.b = BB'
        )

    def test_circular_inject_params(self):

        data = (
            "a.a = ${param:a.a}, "
            "b.a = ${param:b.a}"
        )

        with self.assertRaises(CircularInjectError):
            tplparams.inject(data, params={
                'a.a': '${param:b.a}',
                'b.a': '${param:a.a}',
            })

    def test_circular_inject_params_to_self(self):

        data = "a.a = ${param:a.a}"

        with self.assertRaises(CircularInjectError):
            tplparams.inject(data, params={
                'a.a': '${param:a.a}',
            })

    def test_inject_dict(self):

        data = {
            'database': {
                'host': '${param:hosts.db.ip}',
                'port': '${param:hosts.db.port}',
                'name': 'default',
                'user': 'root',
                'password': ''
            },
            'redis': {
                'url': '${param:hosts.redis.ip}:${param:hosts.redis.port}/1'
            }
        }

        actual = tplparams.inject(data, params={
            'hosts.db.ip': '175.100.11.12',
            'hosts.db.port': 5567,
            'hosts.redis.ip': '111.10.11.12',
            'hosts.redis.port': 6601,
        })

        self.assertDictEqual(actual, {
            'database': {
                'host': '175.100.11.12',
                'port': 5567,
                'name': 'default',
                'user': 'root',
                'password': ''
            },
            'redis': {
                'url': '111.10.11.12:6601/1'
            }
        })
