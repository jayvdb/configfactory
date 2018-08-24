from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import get_objects_for_user

from configfactory.exceptions import ComponentDeleteError
from configfactory.models import Component, Environment, User
from configfactory.services.configsettings import (
    delete_settings,
    get_settings_inject_keys,
)


def get_user_components(user: User):
    if not user.is_authenticated:
        return []
    return get_objects_for_user(
        user=user,
        perms=(
            'view_component',
            'change_component'
        ),
        any_perm=True,
        klass=Component.objects.active()
    )


def delete_component(component: Component):
    """
    Delete component.
    """

    environments = Environment.objects.all()

    for environment in environments:

        inject_keys = get_settings_inject_keys(environment)

        for component_alias, keys in inject_keys.items():

            if component.alias == component_alias:
                continue

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
    for environment in environments:
        delete_settings(environment=environment, component=component)
