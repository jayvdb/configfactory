from guardian.shortcuts import get_objects_for_user

from configfactory.models import Environment


def get_user_environments(user, perms):
    if not user.is_authenticated:
        return []
    return get_objects_for_user(
        user=user,
        perms=perms,
        any_perm=True,
        klass=Environment.objects.active()
    )
