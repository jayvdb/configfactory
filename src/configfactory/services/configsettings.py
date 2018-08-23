import contextlib
import threading
from typing import Dict, Iterable, Set, Union

import dictdiffer
import jsonschema
from django.conf import settings
from django.utils.functional import LazyObject
from django.utils.translation import ugettext_lazy as _

from configfactory.configstore import (
    ConfigStoreBackend,
    DatabaseConfigStore,
    FileSystemConfigStore,
    MemoryConfigStore,
)
from configfactory.exceptions import InvalidSettingsError, InjectKeyError, CircularInjectError
from configfactory.models import Component, Environment
from configfactory.utils import dicthelper, json, security, tplparams


class LazyConfigStoreBackend(LazyObject):

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


_store: ConfigStoreBackend = LazyConfigStoreBackend()
_cached_settings = threading.local()
_cached_settings_key = 'settings'


@contextlib.contextmanager
def use_cached_settings():
    setattr(_cached_settings, _cached_settings_key, get_all_settings())
    yield
    delattr(_cached_settings, _cached_settings_key)


def get_all_settings(decrypt: bool = True):

    if hasattr(_cached_settings, _cached_settings_key):
        return getattr(_cached_settings, _cached_settings_key)

    ret = {}

    for environment, component_data in _store.all_data().items():

        ret[environment] = {}

        for component, data in component_data.items():
            if decrypt:
                ret[environment][component] = security.decrypt_dict(
                    data=json.loads(data),
                    secure_keys=settings.SECURE_KEYS
                )
            else:
                ret[environment][component] = json.loads(data)

    return ret


def get_environment_settings(environment: Environment, components: Iterable[Component] = None) -> dict:

    if components is None:
        components = Component.objects.all()

    return {
        component.alias: get_settings(
            component=component,
            environment=environment
        )
        for component in components
    }


def get_settings(environment: Environment, component: Union[Component, str]) -> dict:
    """
    Get component settings.
    """

    if isinstance(component, Component):
        component_alias = component.alias
    else:
        component_alias = component

    all_settings = get_all_settings()

    if environment.is_base:
        try:
            return all_settings[environment.alias][component_alias]
        except KeyError:
            return {}

    else:

        base_environment = Environment.objects.base().get()

        try:
            base_settings = all_settings[base_environment.alias][component_alias]
        except KeyError:
            base_settings = {}

        try:
            env_settings = all_settings[environment.alias][component_alias]
        except KeyError:
            env_settings = {}

        if environment.fallback:
            try:
                fallback_settings = env_settings[environment.fallback.alias][component_alias]
                env_settings = dicthelper.merge(fallback_settings, env_settings)
            except KeyError:
                pass

        return dicthelper.merge(base_settings, env_settings)


def validate_settings(environment: Environment, component: Component, data: dict):
    """
    Update component settings.
    """

    # Validate changed component referred keys
    setting_keys = list(dicthelper.flatten(
        {component.alias: data}
    ).keys())

    inject_keys = get_settings_inject_keys(
        environment=environment,
        component=component,
        data=data
    )

    for component_alias, keys in inject_keys.items():
        for key in keys:
            if key.startswith(component.alias) and key not in setting_keys:
                raise InvalidSettingsError(
                    _('Component `%s` refers to changed key `%s`.') % (component_alias, key),
                )

    # Validate injections
    try:
        data = inject_settings_params(
            environment=environment,
            data=data,
            strict=True
        )
    except InjectKeyError as exc:
        raise InvalidSettingsError(_('Injected key `%(key)s` does not exist.') % {'key': exc.key})
    except CircularInjectError:
        raise InvalidSettingsError(_('Circular key injections detected.'))
    except Exception:
        raise InvalidSettingsError(_('Unknown settings validation error.'))

    # Validate JSON schema
    if component.require_schema:
        try:
            jsonschema.validate(
                instance=data,
                schema=component.schema
            )
        except (jsonschema.ValidationError, jsonschema.SchemaError) as exc:
            raise InvalidSettingsError(_('Invalid settings schema: %(error)s.') % {'error': exc.message})

    # Validate strict keys
    if component.strict_keys and not environment.is_base:

        base_settings = get_settings(
            environment=Environment.objects.base().get(),
            component=component,
        )

        diff = dictdiffer.diff(base_settings, data)

        add_keys = []
        remove_keys = []

        for summary in diff:
            if 'add' in summary:
                add_keys = [
                    add[0] for add in summary[2]
                    if not isinstance(add[0], int)
                ]
            if 'remove' in summary:
                remove_keys = [
                    remove[0] for remove in summary[2]
                    if not isinstance(remove[0], int)
                ]

        if add_keys:
            raise InvalidSettingsError(
                _('Cannot add new keys to environment configuration. '
                  'New key(s): <b>%(keys)s</b>.') % {
                    'keys': ', '.join(add_keys)
                }
            )

        if remove_keys:
            raise InvalidSettingsError(
                _('Cannot remove keys from environment configuration. '
                  'Removed key(s): <b>%(keys)s</b>.') % {
                    'keys': ', '.join(remove_keys)
                }
            )


def update_settings(environment: Environment, component: Component, data: dict, run_validation: bool = True):
    """
    Update settings.
    """

    if run_validation:
        validate_settings(
            environment=environment,
            component=component,
            data=data,
        )

    if settings.ENCRYPT_ENABLED:
        data = security.encrypt_dict(data, secure_keys=settings.SECURE_KEYS)

    _store.update_data(
        environment=environment.alias,
        component=component.alias,
        data=json.dumps(data, compress=True)
    )


def inject_settings_params(
        environment: Environment,
        data: dict,
        components: Iterable[Component]=None,
        strict: bool=True
) -> dict:

    if components is None:
        components = Component.objects.all()

    # Get filtered environment settings
    params = dicthelper.flatten(
        get_environment_settings(environment, components=components)
    )

    return tplparams.inject(
        data=data,
        params=params,
        strict=strict
    )


def delete_settings(environment: Environment, component: Component):
    """
    Delete settings from store.
    """
    _store.delete_data(environment=environment.alias, component=component.alias)


def get_settings_inject_keys(
        environment: Environment,
        component: Component=None,
        data: dict=None
) -> Dict[str, Set[str]]:
    """
    Get components inject keys.
    """

    if data is None:
        data = {}

    inject_keys = {}
    env_settings = get_environment_settings(environment)

    # Update with changed component settings
    if component:
        env_settings[component.alias] = data

    for component_alias, data in env_settings.items():
        for match in tplparams.param_re.findall(json.dumps(data, compress=True)):
            if component_alias not in inject_keys:
                inject_keys[component_alias] = set()
            key = match[1]
            if key not in inject_keys[component_alias]:
                inject_keys[component_alias].add(key)
    return inject_keys
