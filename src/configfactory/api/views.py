from distutils.util import strtobool

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View

from configfactory.mixins import ConfigStoreCachedMixin
from configfactory.models import Component, Environment
from configfactory.services.configsettings import (
    get_environment_settings,
    get_settings,
    inject_settings_params,
)
from configfactory.utils import dicthelper


class EnvironmentsAPIView(View):

    def get(self, request):

        data = [{
            'alias': environment.alias,
            'name': environment.name,
            'fallback': environment.fallback.alias if environment.fallback_id else None,
            'url': request.build_absolute_uri(
                reverse('api_components', kwargs={
                    'environment': environment.alias
                })
            )
        } for environment in Environment.objects.active()]

        return JsonResponse(data=data, safe=False)


class ComponentsAPIView(ConfigStoreCachedMixin, View):

    def get(self, request, environment):

        environment = get_object_or_404(Environment, alias=environment)
        flatten = _get_flatten_param(request)

        components = list(Component.objects.all())

        data = get_environment_settings(environment, components=components)

        if flatten:
            data = dicthelper.flatten(data)

        data = inject_settings_params(
            environment=environment,
            data=data,
            components=components,
            strict=False
        )

        return JsonResponse(data, safe=False)


class ComponentSettingsAPIView(ConfigStoreCachedMixin, View):

    def get(self, request, environment, alias):

        component = get_object_or_404(Component, alias=alias)
        environment = get_object_or_404(Environment, alias=environment)
        flatten = _get_flatten_param(request)

        data = get_settings(
            environment=environment,
            component=component,
        )

        if flatten:
            data = dicthelper.flatten(data)

        return JsonResponse(data=data, safe=False)


def _get_flatten_param(request):
    try:
        return bool(strtobool(request.GET.get('flatten', 'no').lower()))
    except ValueError:
        return False
