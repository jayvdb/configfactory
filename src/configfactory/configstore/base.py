import contextlib
import threading
from typing import Dict, Union, List, Set

# from django.conf import settings
from django.utils.functional import cached_property

from configfactory.models import Component, Environment
from configfactory.utils import dicthelper, json, security, tplparams

from .backends.base import ConfigStoreBackend
from .backends.database import DatabaseConfigStore
from .backends.filesystem import FileSystemConfigStore
from .backends.memory import MemoryConfigStore


class ConfigStore:

    backend_registry = {
        'memory': MemoryConfigStore,
        'filesystem': FileSystemConfigStore,
        'database': DatabaseConfigStore
    }

    def __init__(self, backend: ConfigStoreBackend, encrypt_enabled: bool=False, secure_keys: List[str]=None):
        self._backend = backend
        self._encrypt_enabled = encrypt_enabled
        self._secure_keys = secure_keys or []
        self._cache = threading.local()

    @property
    def backend(self) -> ConfigStoreBackend:
        return self._backend

    @property
    def encrypt_enabled(self) -> bool:
        return self._encrypt_enabled

    @property
    def secure_keys(self) -> List[str]:
        return self._secure_keys

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

    def all(self, decrypt: bool=True) -> Dict[str, Dict[str, dict]]:
        """
        Get all settings.
        """
        # Return cached settings
        if self.cached():
            return getattr(self._cache, 'cache')

        all_data = {}

        for environment, component_data in self.backend.all_data().items():

            all_data[environment] = {}

            for component, data in component_data.items():
                if decrypt:
                    all_data[environment][component] = security.decrypt_dict(
                        data=json.loads(data),
                        secure_keys=self.secure_keys
                    )
                else:
                    all_data[environment][component] = json.loads(data)

        return all_data

    def env(self, environment: Union[Environment, str]) -> dict:
        """
        Get environment settings.
        """
        if isinstance(environment, Environment):
            environment = environment.alias
        try:
            return self.all()[environment]
        except KeyError:
            return {}

    def get(self, environment: Union[Environment, str], component: Union[Component, str]) -> dict:
        """
        Get settings.
        """

        if isinstance(environment, str):
            environment = Environment.objects.get(alias=environment)

        if isinstance(component, Component):
            component = component.alias

        all_data = self.all()

        if environment.is_base:
            try:
                return all_data[environment.alias][component]
            except KeyError:
                return {}

        else:

            try:
                base_data = all_data[self.base_environment.alias][component]
            except KeyError:
                base_data = {}

            try:
                env_data = all_data[environment.alias][component]
            except KeyError:
                env_data = {}

            if environment.fallback:

                try:
                    fallback_data = all_data[environment.fallback.alias][component]
                    env_data = dicthelper.merge(fallback_data, env_data)
                except KeyError:
                    pass

            return dicthelper.merge(base_data, env_data)

    def update(self, environment: Union[Environment, str], component: Union[Component, str], data: dict):
        """
        Update settings.
        """

        if isinstance(environment, Environment):
            environment = environment.alias

        if isinstance(component, Component):
            component = component.alias

        if not isinstance(data, dict):
            raise TypeError("`settings` must be dict type.")

        if self.encrypt_enabled:
            data = security.encrypt_dict(data, secure_keys=self.secure_keys)

        self.backend.update_data(
            environment=environment,
            component=component,
            data=json.dumps(data, compress=True)
        )

    def delete(self, environment: Union[Environment, str], component: Union[Component, str]):
        """
        Delete component settings.
        """

        if isinstance(environment, Environment):
            environment = environment.alias

        if isinstance(component, Component):
            component = component.alias

        self.backend.delete_data(environment=environment, component=component)

    def normalize(self):
        """
        Normalize ConfigStore data.
        """

        for environment, components_data in self.all().items():
            for component, data in components_data.items():
                if not Environment.objects.filter(alias=environment).exists():
                    self.backend.delete_data(environment=environment, component=component)
                    continue
                if not Component.objects.filter(alias=component).exists():
                    self.backend.delete_data(environment=environment, component=component)
                    continue
                self.update(environment, component, data=data)

    def get_inject_keys(self, environment: str, component: str=None, data: dict=None) -> Dict[str, Set[str]]:
        """
        Get components inject keys.
        """

        keys = {}
        env_data = self.env(environment)

        # Update with changed component settings
        if component:
            if data is None:
                data = {}
            env_data[component] = data

        for component, data in env_data.items():
            for match in tplparams.param_re.findall(json.dumps(data, compress=True)):
                if component not in keys:
                    keys[component] = set()
                key = match[1]
                if key not in keys[component]:
                    keys[component].add(key)
        return keys
