import pytest

from configfactory.configstore import MemoryConfigStore


@pytest.fixture()
def store():
    return MemoryConfigStore()


def test_empty_data(store: MemoryConfigStore):
    assert not store.get_all_data()


def test_update_data(store: MemoryConfigStore):
    store.update_data('dev', 'db', {
        'uri': 'localhost:3722'
    })

    assert store.get_all_data() == {
        'dev': {
            'db': {
                'uri': 'localhost:3722'
            }
        }
    }


def test_get_data(store: MemoryConfigStore):
    store.update_data('dev', 'db', {
        'uri': 'localhost:3722'
    })

    assert store.get_data('dev', 'db') == {
        'uri': 'localhost:3722'
    }


def test_delete_data(store: MemoryConfigStore):
    store.update_data('dev', 'db', {
        'uri': 'localhost:3722'
    })

    assert store.get_data('dev', 'db')

    store.delete_data('dev', 'db')

    assert not store.get_data('dev', 'db')
