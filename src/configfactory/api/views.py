from distutils.util import strtobool

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View

from configfactory.mixins import ConfigStoreCachedMixin
from configfactory.models import Environment
from configfactory.response import DotEnvResponse
from configfactory.services.configsettings import get_environment_settings
from configfactory.utils import dicthelper


class EnvironmentsAPIView(View):

    def get(self, request):

        data = [{
            'alias': environment.alias,
            'name': environment.name,
            'fallback': environment.fallback.alias if environment.fallback_id else None,
            'url': request.build_absolute_uri(
                reverse('api:settings', kwargs={
                    'environment': environment.alias
                })
            )
        } for environment in Environment.objects.active()]

        return JsonResponse(data=data, safe=False)


class SettingsJsonAPIView(ConfigStoreCachedMixin, View):

    def get(self, request, environment):

        environment = get_object_or_404(Environment, alias=environment)
        flatten = _get_flatten_param(request)

        data = get_environment_settings(environment)

        if flatten:
            data = dicthelper.flatten(data)

        return JsonResponse(data=data, safe=False)


class SettingsDotEnvAPIView(ConfigStoreCachedMixin, View):

    def get(self, request, environment):

        environment = get_object_or_404(Environment, alias=environment)

        data = get_environment_settings(environment)

        return DotEnvResponse(data=data)


def _get_flatten_param(request):
    try:
        return bool(strtobool(request.GET.get('flatten', 'no').lower()))
    except ValueError:
        return False
