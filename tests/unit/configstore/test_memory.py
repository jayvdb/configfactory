import pytest

from configfactory.configstore import MemoryConfigStore


@pytest.fixture()
def store():
    return MemoryConfigStore()


def test_empty_data(store: MemoryConfigStore):
    assert not store.get_all_data()


def test_update_and_get_data(store: MemoryConfigStore):
    store.update_data('dev', 'db', 'dev:db:data')

    assert store.get_all_data() == {
        'dev': {
            'db': 'dev:db:data'
        }
    }


def test_delete_data(store: MemoryConfigStore):
    store.update_data('dev', 'db', 'dev:db:data')
    store.delete_data('dev', 'db')

    assert store.get_all_data() == {
        'dev': {}
    }
