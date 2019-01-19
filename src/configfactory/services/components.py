from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import get_objects_for_user

from configfactory.exceptions import ComponentDeleteError
from configfactory.models import Component, Environment, User
from configfactory.services.configsettings import (
    delete_settings,
    get_settings_referred_keys,
)
from configfactory.signals import component_deleted


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


def delete_component(component: Component, user: User = None):
    """
    Delete component.
    """

    environments = Environment.objects.all()

    for environment in environments:

        referred_keys = get_settings_referred_keys(environment, component=component)

        for component_alias, keys in referred_keys.items():
            raise ComponentDeleteError(
                _('Component `%(component)s` is referring to component `%(key)s` key(s).') % {
                    'component': component_alias,
                    'key': ', '.join(keys)
                }
            )

    # Delete database row
    component.delete()

    # Delete from config store
    for environment in environments:
        delete_settings(environment=environment, component=component)

    # Notify about deleted component
    component_deleted.send(sender=Component, component=component, user=user)
