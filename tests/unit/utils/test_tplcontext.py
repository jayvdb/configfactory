import json

import pytest

from configfactory.utils import tplcontext


def test_inject_string():

    template = "a = ${a}"

    actual = tplcontext.inject(template, context={
        'a': 'TEST'
    })

    assert actual == "a = TEST"


def test_inject_missing_key_raise_exception():

    template = "a = ${a}"

    with pytest.raises(tplcontext.InvalidKey) as exc_info:
        tplcontext.inject(template, context={
            'b': 'TEST'
        }, strict=True)

    exc: tplcontext.InvalidKey = exc_info.value

    assert str(exc) == 'Injected key `a` does not exist.'
    assert exc.key == 'a'


def test_inject_missing_key_ignore_exception():

    template = "a = ${a}"

    actual = tplcontext.inject(template, context={
        'b': 'TEST'
    }, strict=False)

    assert actual == 'a = ${a}'


def test_inject_keep_data_type():

    template = "${a}"

    actual = tplcontext.inject(template, context={
        'a': 100
    })

    assert actual == 100


def test_inject_non_string():

    template = 100

    actual = tplcontext.inject(template, context={
        'a': 000
    })

    assert actual == 100


def test_inject_keys():

    template = (
        "a.b.c = ${a.b.c}, "
        "b.c = ${b.c}, "
        "c.d.e = ${c.d.e}"
    )

    actual = tplcontext.inject(template, context={
        'a.b.c': 'ABC',
        'b.c': '${a.b.c}:BC',
        'c.d': 'CD',
        'c.d.e': '${b.c}:${c.d}',
    })

    assert actual == "a.b.c = ABC, b.c = ABC:BC, c.d.e = ABC:BC:CD"


def test_inject_key_to_self():

    template = (
        "db.host = ${db.host}, "
        "db.default.host = ${db.host}"
    )

    actual = tplcontext.inject(template, context={
        'db.host': 'localhost',
        'db.default.host': '${db.host}',
    })

    assert actual == "db.host = localhost, db.default.host = localhost"


def test_inject_keys_to_each_other():

    template = (
        "a.a = ${a.a}, "
        "a.b = ${a.b}, "
        "b.a = ${b.a}, "
        "b.b = ${b.b}"
    )

    actual = tplcontext.inject(template, context={
        'a.a': 'AA',
        'a.b': '${b.b}',
        'b.a': '${a.b}',
        'b.b': 'BB',
    })

    assert actual == 'a.a = AA, a.b = BB, b.a = BB, b.b = BB'


def test_circular_inject():

    data = (
        "a.a = ${a.a}, "
        "b.a = ${b.a}"
    )

    with pytest.raises(tplcontext.CircularInjectError) as exc_info:
        tplcontext.inject(data, context={
            'a.a': '${b.a}',
            'b.a': '${a.a}',
        })

    exc: tplcontext.CircularInjectError = exc_info.value

    assert str(exc) == 'Circular injections detected.'


def test_circular_inject_self_keys():

    data = "a.a = ${a.a}"

    with pytest.raises(tplcontext.CircularInjectError) as exc_info:
        tplcontext.inject(data, context={
            'a.a': '${a.a}',
        })

    exc: tplcontext.CircularInjectError = exc_info.value

    assert str(exc) == 'Circular injections detected.'


def test_inject_dict():

    template = {
        'database': {
            'host': '${hosts.db.ip}',
            'port': '${hosts.db.port}',
            'name': 'default',
            'user': 'root',
            'password': ''
        },
        'redis': {
            'url': '${hosts.redis.ip}:${hosts.redis.port}/1'
        }
    }

    actual = tplcontext.inject(template, context={
        'hosts.db.ip': '175.100.11.12',
        'hosts.db.port': 5567,
        'hosts.redis.ip': '111.10.11.12',
        'hosts.redis.port': 6601,
    })

    assert actual == {
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
    }


def test_keys():

    template = {
        'database': {
            'host': '${hosts.db.ip}',
            'port': '${hosts.db.port}',
            'name': 'default',
            'user': 'root',
            'password': ''
        },
        'redis': {
            'url': '${hosts.redis.ip}:${hosts.redis.port}/1'
        }
    }

    keys = tplcontext.findkeys(json.dumps(template))

    assert keys == {
        'hosts.db.ip',
        'hosts.db.port',
        'hosts.redis.ip',
        'hosts.redis.port'
    }
