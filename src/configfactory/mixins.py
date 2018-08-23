from django.contrib.auth.mixins import UserPassesTestMixin

from configfactory.services.configsettings import use_cached_settings


class SuperuserRequiredMixin(UserPassesTestMixin):

    raise_exception = True

    def test_func(self):
        return self.request.user.is_superuser


class ConfigStoreCachedMixin:

    def dispatch(self, request, *args, **kwargs):
        with use_cached_settings():
            return super().dispatch(request, *args, **kwargs)
