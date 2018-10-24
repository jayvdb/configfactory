from distutils.util import strtobool

from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import View

from configfactory.mixins import ConfigStoreCachedMixin
from configfactory.models import Environment
from configfactory.response import DotEnvResponse
from configfactory.services.configsettings import get_environment_settings
from configfactory.services.environments import (
    get_user_or_group_view_environments,
)
from configfactory.utils import dicthelper


class APIView(View):

    def dispatch(self, request, *args, **kwargs):
        if not getattr(request, 'api_identity', None):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def environments(self):
        return get_user_or_group_view_environments(user_or_group=self.request.api_identity)


class EnvironmentsAPIView(APIView):

    def get(self, request):

        data = [
            self._render(request, environment)
            for environment in self.environments
        ]

        return JsonResponse(data=data, safe=False)

    def _render(self, request, environment: Environment):
        return {
            'alias': environment.alias,
            'name': environment.name,
            'fallback': environment.fallback.alias if environment.fallback_id else None,
            'url': request.build_absolute_uri(
                reverse('api:settings', kwargs={
                    'environment': environment.alias
                })
            )
        }


class SettingsAPIView(ConfigStoreCachedMixin, APIView):

    def get(self, request, environment):
        environment = get_object_or_404(self.environments, alias=environment)
        data = get_environment_settings(environment)
        return self.render_response(request, data)

    def render_response(self, request, data: dict) -> HttpResponse:
        raise NotImplemented


class SettingsJsonAPIView(SettingsAPIView):

    def render_response(self, request, data: dict) -> HttpResponse:
        try:
            flatten = bool(strtobool(request.GET.get('flatten', 'no').lower()))
        except ValueError:
            flatten = False
        if flatten:
            data = dicthelper.flatten(data)
        return JsonResponse(data=data, safe=False)


class SettingsDotEnvAPIView(SettingsAPIView):

    def render_response(self, request, data: dict) -> HttpResponse:
        return DotEnvResponse(data=data)
