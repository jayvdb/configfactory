from typing import Iterable, Union

from django.contrib.auth.models import Group
from guardian.shortcuts import get_objects_for_group, get_objects_for_user

from configfactory.models import Environment, User


def get_user_environments(user: User, perms: Iterable[str]):
    if not user.is_authenticated:
        return []
    return get_objects_for_user(
        user=user,
        perms=perms,
        any_perm=True,
        klass=Environment.objects.active()
    )


def get_user_view_environments(user: User):
    return get_user_environments(user, perms=(
        'view_environment',
    ))


def get_user_change_environments(user: User):
    return get_user_environments(user, perms=(
        'change_environment',
    ))


def get_user_or_group_view_environments(user_or_group: Union[User, Group]):

    environments = Environment.objects.active()
    perms = ('view_environment',)

    if isinstance(user_or_group, Group):
        return get_objects_for_group(
            group=user_or_group,
            perms=perms,
            any_perm=True,
            klass=environments
        )

    return get_objects_for_user(
        user=user_or_group,
        perms=perms,
        any_perm=True,
        klass=environments
    )
