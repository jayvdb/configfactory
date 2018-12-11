import pytest

from configfactory.configstore import MemoryConfigStore


@pytest.fixture()
def store():
    return MemoryConfigStore()


def test_empty_data(store: MemoryConfigStore):
    assert not store.all()


def test_update_data(store: MemoryConfigStore):
    store.update('dev', 'db', 'dev:db:data')

    assert store.all() == {
        'dev': {
            'db': 'dev:db:data'
        }
    }


def test_delete_data(store: MemoryConfigStore):
    store.update('dev', 'db', 'dev:db:data')
    store.delete('dev', 'db')

    assert store.all() == {
        'dev': {}
    }
