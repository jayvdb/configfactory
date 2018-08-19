from django.utils.functional import LazyObject

from configfactory import settings
from configfactory.configstore.backends.database import DatabaseConfigStore
from configfactory.configstore.backends.filesystem import FileSystemConfigStore
from configfactory.configstore.backends.memory import MemoryConfigStore
from configfactory.configstore.base import ConfigStore

from .base import ConfigStore


class ConfigStoreHandler(LazyObject):

    registry = {
        'memory': MemoryConfigStore,
        'filesystem': FileSystemConfigStore,
        'database': DatabaseConfigStore
    }

    def _setup(self):
        backend_class = self.registry[settings.CONFIGSTORE_BACKEND]
        if settings.CONFIGSTORE_OPTIONS:
            backend_instance = backend_class(**settings.CONFIGSTORE_OPTIONS)
        else:
            backend_instance = backend_class()
        self._wrapped = ConfigStore(
            backend=backend_instance,
            encrypt_enabled=settings.ENCRYPT_ENABLED,
            secure_keys=settings.SECURE_KEYS
        )


# Set default config store
_instance: ConfigStore = ConfigStoreHandler()
backend = _instance.backend
cachecontext = _instance.cachecontext
all_data = _instance.all
env = _instance.env
get = _instance.get
update = _instance.update
delete = _instance.delete
normalize = _instance.normalize
ikeys = _instance.ikeys
