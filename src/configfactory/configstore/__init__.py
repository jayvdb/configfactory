import contextlib
import threading
from typing import Dict

from django.conf import settings
from django.utils.functional import LazyObject

from configfactory.configstore.base import ConfigStore
from configfactory.configstore.database import DatabaseConfigStore
from configfactory.configstore.filesystem import FileSystemConfigStore
from configfactory.configstore.memory import MemoryConfigStore
from configfactory.utils import dictutil, iterutil, json

_cached_data = threading.local()
_cached_data_key = 'settings'


class ConfigStoreSetup(LazyObject):

    def _setup(self):
        backend = settings.CONFIGSTORE_BACKEND
        if backend == 'filesystem':
            instance = FileSystemConfigStore(settings.CONFIGSTORE_DIRECTORY)
        elif backend == 'database':
            instance = DatabaseConfigStore()
        else:
            instance = MemoryConfigStore()
        self._wrapped = instance


_store: ConfigStore = ConfigStoreSetup()


#########################################
# Public API
#########################################
@contextlib.contextmanager
def cached_data():
    setattr(_cached_data, _cached_data_key, get_all_data())
    yield
    delattr(_cached_data, _cached_data_key)


def get_all_data() -> Dict[str, Dict[str, dict]]:
    if hasattr(_cached_data, _cached_data_key):
        return getattr(_cached_data, _cached_data_key)
    data = _store.all()
    return iterutil.traverse(data, lambda value, path: json.loads(value))


def update_data(environment: str, component: str, data: dict):
    _store.update(
        environment=environment,
        component=component,
        data=json.dumps(data, compress=True)
    )


def delete_data(environment: str, component: str):
    _store.delete(environment=environment, component=component)
