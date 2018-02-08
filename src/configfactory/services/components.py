from typing import Iterable

import dictdiffer
import jsonschema
from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import get_objects_for_user

from configfactory import configstore
from configfactory.exceptions import (
    ComponentDeleteError,
    ComponentValidationError,
    InjectKeyError,
)
from configfactory.models import Component, Environment
from configfactory.utils import dicthelper, tplparams


def get_user_components(user):
    if not user.is_authenticated:
        return []
    return get_objects_for_user(
        user=user,
        perms=('view_component', 'change_component'),
        any_perm=True,
        klass=Component.objects.active()
    )


def get_environment_settings(environment: Environment, components: Iterable[Component] = None) -> dict:

    if components is None:
        components = Component.objects.all()

    return {
        component.alias: get_component_settings(component, environment=environment)
        for component in components
    }


def prepare_component_settings_data(component: Component, environment: Environment):
    return {
        'settings': {
            environment.alias: configstore.backend.get_data(
                environment=environment.alias,
                component=component.alias
            )
        }
    }


def get_component_settings(component: Component, environment: Environment):
    """
    Get component settings.
    """

    return configstore.get(
        environment=environment,
        component=component
    )


def update_component_settings(component: Component,
                              environment: Environment,
                              settings: dict,
                              skip_validation=False
                              ) -> Component:

    if not skip_validation:
        validate_component_settings(
            component=component,
            environment=environment,
            settings=settings,
        )

    configstore.update(
        environment=environment,
        component=component,
        data=settings
    )

    return component


def validate_component_settings(component: Component, environment: Environment, settings: dict):
    """
    Update component settings.
    """

    # Validate changed component referred keys
    setting_keys = list(dicthelper.flatten(
        {component.alias: settings}
    ).keys())

    components_keys = configstore.ikeys(
        environment=environment,
        component=component,
        settings=settings
    )

    for component_alias, keys in components_keys.items():
        for key in keys:
            if key.startswith(component.alias) and key not in setting_keys:
                exc = InjectKeyError('error', key=key)
                raise ComponentValidationError(
                    _('Component `%s` refers to changed key `%s`.') % (
                        component_alias,
                        key
                    ),
                    exc=exc
                )

    # Validate injections
    try:
        data = inject_params(
            environment=environment,
            settings=settings,
            strict=True
        )
    except InjectKeyError as exc:
        raise ComponentValidationError(str(exc), exc=exc)

    # Validate JSON schema
    if component.require_schema:
        try:
            jsonschema.validate(
                instance=data,
                schema=component.schema
            )
        except (jsonschema.ValidationError, jsonschema.SchemaError) as exc:
            raise ComponentValidationError(
                _('Invalid settings schema: %s') % exc,
                exc=exc
            )

    # Validate strict keys
    if component.strict_keys and not environment.is_base:

        base_settings = get_component_settings(
            component=component,
            environment=Environment.objects.base().get()
        )

        diff = dictdiffer.diff(base_settings, settings)

        add_keys = []
        remove_keys = []

        for summary in diff:
            if 'add' in summary:
                add_keys = [
                    add[0] for add in summary[2]
                ]
            if 'remove' in summary:
                remove_keys = [
                    remove[0] for remove in summary[2]
                ]

        if add_keys:
            raise ComponentValidationError(
                _('Cannot add new keys to environment configuration. '
                  'New key(s): <b>%(keys)s</b>.') % {
                    'keys': ', '.join(add_keys)
                }
            )

        if remove_keys:
            raise ComponentValidationError(
                _('Cannot remove keys from environment configuration. '
                  'Removed key(s): <b>%(keys)s</b>.') % {
                    'keys': ', '.join(remove_keys)
                }
            )


def delete_component(component: Component):
    """
    Delete component.
    """

    for environment in Environment.objects.all():

        inject_keys = configstore.ikeys(environment)

        for component_alias, keys in inject_keys.items():

            referred_keys = list(
                filter(lambda k: k.startswith(component.alias), keys)
            )

            if referred_keys:
                raise ComponentDeleteError(
                    _('Component `%(component)s` is referring to component `%(key)s` key.') % {
                        'component': component_alias,
                        'key': referred_keys[0]
                    }
                )

    # Delete database row
    component.delete()

    # Delete from config store
    configstore.delete(component)


def inject_params(environment, settings, components=None, strict=True):

    if components is None:
        components = Component.objects.all()

    # Get filtered environment settings
    params = dicthelper.flatten(get_environment_settings(environment, components=components))

    return tplparams.inject(
        data=settings,
        params=params,
        strict=strict
    )
