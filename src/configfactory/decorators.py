from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def superuser_required(view_func=None, raise_exception=True):
    def check_flag(user):
        if user.is_active and user.is_superuser:
            return True
        if raise_exception:
            raise PermissionDenied
        return False
    actual_decorator = user_passes_test(check_flag)
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
