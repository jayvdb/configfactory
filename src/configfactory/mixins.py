from django.contrib.auth.mixins import UserPassesTestMixin

from configfactory import configstore


class SuperuserRequiredMixin(UserPassesTestMixin):

    raise_exception = True

    def test_func(self):
        return self.request.user.is_superuser


class ConfigStoreCachedMixin:

    def dispatch(self, request, *args, **kwargs):
        with configstore.cachecontext():
            return super().dispatch(request, *args, **kwargs)
