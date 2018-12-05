from typing import Dict, Iterable, Set, Union

import dictdiffer
import jsonschema
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from configfactory import configstore
from configfactory.exceptions import (
    CircularInjectError,
    InjectKeyError,
    InvalidSettingsError,
)
from configfactory.models import Component, Environment
from configfactory.utils import dicthelper, json, security, tplparams
from configfactory.validators import validate_settings_format


def get_all_settings() -> Dict[str, Dict[str, dict]]:
    """
    Get all settings.
    """

    all_data = configstore.get_all_data()

    if settings.ENCRYPT_ENABLED:
        return security.decrypt(data=all_data, secure_keys=settings.SECURE_KEYS)

    return all_data


def get_environment_settings(environment: Environment, components: Iterable[Component] = None) -> dict:
    """
    Get environment settings.
    """

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

    # Validate settings format
    try:
        validate_settings_format(data)
    except ValidationError as exc:
        raise InvalidSettingsError(exc.message)

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
        data = security.encrypt(data, secure_keys=settings.SECURE_KEYS)

    configstore.update_data(environment=environment.alias, component=component.alias, data=data)


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
    configstore.delete_data(environment=environment.alias, component=component.alias)


def cleanup_settings():
    """
    Cleanup settings.
    """
    for environment, components_data in configstore.get_all_data().items():
        for component, data in components_data.items():
            if not Environment.objects.filter(alias=environment).exists():
                configstore.delete_data(environment=environment, component=component)
                continue
            if not Component.objects.filter(alias=component).exists():
                configstore.delete_data(environment=environment, component=component)
                continue
            configstore.update_data(environment=environment, component=component, data=data)


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
