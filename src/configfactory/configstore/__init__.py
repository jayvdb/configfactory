from typing import Dict

from django.conf import settings
from django.utils.functional import LazyObject

from configfactory.configstore.base import ConfigStore
from configfactory.configstore.database import DatabaseConfigStore
from configfactory.configstore.filesystem import FileSystemConfigStore
from configfactory.configstore.memory import MemoryConfigStore
from configfactory.utils import json


class ConfigStoreSetup(LazyObject):

    registry = {
        'memory': MemoryConfigStore,
        'filesystem': FileSystemConfigStore,
        'database': DatabaseConfigStore
    }

    def _setup(self):
        klass = self.registry[settings.CONFIGSTORE_BACKEND]
        if settings.CONFIGSTORE_OPTIONS:
            instance = klass(**settings.CONFIGSTORE_OPTIONS)
        else:
            instance = klass()
        self._wrapped = instance


_store: ConfigStore = ConfigStoreSetup()


#########################################
# Public API
#########################################

def get_all_data() -> Dict[str, Dict[str, dict]]:
    ret = {}
    for environment, component_data in _store.get_all_data().items():
        ret[environment] = {}
        for component, data in component_data.items():
            ret[environment][component] = json.loads(data)
    return ret


def update_data(environment: str, component: str, data: dict):
    _store.update_data(
        environment=environment,
        component=component,
        data=json.dumps(data, compress=True)
    )


def delete_data(environment: str, component: str):
    _store.delete_data(environment=environment, component=component)
