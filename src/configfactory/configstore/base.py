import contextlib
import threading
from typing import Dict

from django.conf import settings

from configfactory.models import Environment, Component
from configfactory.utils import json, tplparams
from configfactory.utils.security import decrypt_data, encrypt_data

from .backends.base import ConfigStoreBackend
from .backends.database import DatabaseConfigStore
from .backends.memory import MemoryConfigStore

BACKEND_REGISTRY = {
    'memory': MemoryConfigStore,
    'database': DatabaseConfigStore
}


class ConfigStore:

    def __init__(self, backend):
        self.backend = backend  # type: ConfigStoreBackend
        self._cache = threading.local()

    @classmethod
    def configure(cls) -> 'ConfigStore':
        backend_type = settings.CONFIG_STORE['backend']
        backend_class = BACKEND_REGISTRY[backend_type]
        backend_options = settings.CONFIG_STORE.get('options', {})
        if backend_options:
            backend = backend_class(**backend_options)
        else:
            backend = backend_class()
        return ConfigStore(backend)

    @contextlib.contextmanager
    def cachecontext(self):
        setattr(self._cache, 'cache', self.all_settings())
        yield self
        delattr(self._cache, 'cache')

    def cached(self):
        return hasattr(self._cache, 'cache')

    def all_settings(self) -> Dict[str, Dict[str, dict]]:
        """
        Get all settings.
        """
        # Return cached settings
        if self.cached():
            return getattr(self._cache, 'cache')

        all_settings = {}
        for environment, component_data in self.backend.all_data().items():
            all_settings[environment] = {}
            for component, data in component_data.items():
                settings = json.loads(decrypt_data(data))
                all_settings[environment][component] = settings
        return all_settings

    def env_settings(self, environment):
        """
        Get environment settings.
        """
        all_settings = self.all_settings()
        return all_settings.get(environment, {})

    def get_settings(self, environment, component):
        """
        Get settings.
        """

        # Return cached settings
        if self.cached():
            cache = getattr(self._cache, 'cache')
            return cache.get(environment, {}).get(component, {})

        data = self.backend.get_data(environment, component)
        if data is None:
            return {}
        return json.loads(decrypt_data(data))

    def update_settings(self, environment: str, component: str, settings: dict):
        """
        Update settings.
        """
        # Prepare settings string
        if isinstance(settings, (dict, list)):
            settings = json.dumps(settings, compress=True)
        data = encrypt_data(settings)
        self.backend.update_data(environment, component, data)

    def delete_settings(self, component: Component):
        """
        Delete component settings.
        """
        environments = self.all_settings().keys()
        for environment in environments:
            self.backend.delete_data(
                environment=environment,
                component=component.alias
            )

    def inject_keys(self, environment: Environment, component: Component = None, settings: dict = None):
        """
        Get components inject keys.
        """

        keys = {}
        env_settings = self.env_settings(environment)

        # Update with changed component settings
        if component:
            if settings is None:
                settings = {}
            env_settings[component] = settings

        for component, data in env_settings.items():
            for match in tplparams.param_re.findall(json.dumps(data, compress=True)):
                if component not in keys:
                    keys[component] = []
                key = match[1]
                if key not in keys[component]:
                    keys[component].append(key)
        return keys
