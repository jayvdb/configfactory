from typing import Union

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from guardian.shortcuts import assign_perm, remove_perm

from configfactory.models import User

ACTION_ASSIGN = 'assign'
ACTION_REMOVE = 'remove'


def update_permission(user_or_group: Union[User, Group], obj: Model, perm: str, action: str):

    content_type = ContentType.objects.get_for_model(obj)

    # Get or create permission
    try:
        permission = Permission.objects.get(content_type=content_type, codename=perm)
    except Permission.DoesNotExist:
        name = perm.replace('_', '').title()
        permission = Permission.objects.create(
            name='Can %s %s' % (name, obj._meta.verbose_name_raw),
            content_type=content_type,
            codename=perm
        )

    if action == ACTION_ASSIGN:
        assign_perm(permission, user_or_group, obj)
    else:
        remove_perm(permission, user_or_group, obj)


def assign_permission(user_or_group: Union[User, Group], obj: Model, perm: str):
    update_permission(
        user_or_group=user_or_group,
        obj=obj,
        perm=perm,
        action=ACTION_ASSIGN
    )


def remove_permission(user_or_group: Union[User, Group], obj: Model, perm: str):
    update_permission(
        user_or_group=user_or_group,
        obj=obj,
        perm=perm,
        action=ACTION_REMOVE
    )
