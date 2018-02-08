import contextlib
import threading
from typing import Dict

from django.conf import settings
from django.utils.functional import cached_property

from configfactory.models import Component, Environment
from configfactory.utils import json, security, tplparams, dicthelper

from .backends.base import ConfigStoreBackend
from .backends.database import DatabaseConfigStore
from .backends.memory import MemoryConfigStore


class ConfigStore:

    backend_registry = {
        'memory': MemoryConfigStore,
        'database': DatabaseConfigStore
    }

    secured_keys = settings.SECURED_KEYS

    encrypt_enabled = settings.ENCRYPT_ENABLED

    def __init__(self, backend: ConfigStoreBackend):
        self.backend = backend
        self._cache = threading.local()

    @classmethod
    def configure(cls) -> 'ConfigStore':
        backend_class = cls.backend_registry[settings.CONFIGSTORE_BACKEND]
        if settings.CONFIGSTORE_OPTIONS:
            backend = backend_class(**settings.CONFIGSTORE_OPTIONS)
        else:
            backend = backend_class()
        return ConfigStore(backend)

    @contextlib.contextmanager
    def cachecontext(self):
        setattr(self._cache, 'cache', self.all())
        yield self
        delattr(self._cache, 'cache')

    def cached(self):
        return hasattr(self._cache, 'cache')

    @cached_property
    def base_environment(self) -> Environment:
        return Environment.objects.base().get()

    def all(self) -> Dict[str, Dict[str, dict]]:
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
                all_settings[environment][component] = security.decrypt_dict(
                    data=json.loads(data),
                    secured_keys=settings.SECURED_KEYS
                )
        return all_settings

    def env(self, environment: Environment) -> dict:
        """
        Get environment settings.
        """
        try:
            return self.all()[environment.alias]
        except KeyError:
            return {}

    def get(self, environment: Environment, component: Component) -> dict:
        """
        Get settings.
        """

        all_settings = self.all()

        if environment.is_base:
            try:
                return all_settings[environment.alias][component.alias]
            except KeyError:
                return {}

        else:

            try:
                base_settings = all_settings[self.base_environment.alias][component.alias]
            except KeyError:
                base_settings = {}

            try:
                env_settings = all_settings[environment.alias][component.alias]
            except KeyError:
                env_settings = {}

            if environment.fallback:

                try:
                    fallback_settings = all_settings[environment.fallback.alias][component.alias]
                    env_settings = dicthelper.merge(fallback_settings, env_settings)
                except KeyError:
                    pass

            return dicthelper.merge(base_settings, env_settings)

    def update(self, environment: Environment, component: Component, data: dict):
        """
        Update settings.
        """

        if not isinstance(data, dict):
            raise TypeError("`settings` must be dict type.")

        if self.encrypt_enabled:
            data = security.encrypt_dict(data, secured_keys=settings.SECURED_KEYS)

        self.backend.update_data(
            environment=environment.alias,
            component=component.alias,
            data=json.dumps(data, compress=True)
        )

    def delete(self, component: Component):
        """
        Delete component settings.
        """
        environments = self.all().keys()
        for environment in environments:
            self.backend.delete_data(
                environment=environment,
                component=component.alias
            )

    def ikeys(self, environment: Environment, component: Component = None, settings: dict = None):
        """
        Get components inject keys.
        """

        keys = {}
        env_settings = self.env(environment)

        # Update with changed component settings
        if component:
            if settings is None:
                settings = {}
            env_settings[component] = settings

        for component, data in env_settings.items():
            for match in tplparams.param_re.findall(json.dumps(data, compress=True)):
                if component not in keys:
                    keys[component] = set()
                key = match[1]
                if key not in keys[component]:
                    keys[component].add(key)
        return keys
