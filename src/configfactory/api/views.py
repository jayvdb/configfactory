from django.utils.functional import cached_property
from rest_framework.generics import get_object_or_404
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView as BaseAPIView

from configfactory.api.authentication import TokenAuthentication
from configfactory.api.permissions import IsAuthenticated
from configfactory.api.renderers import DotEnvRenderer
from configfactory.api.serializers import EnvironmentSerializer
from configfactory.mixins import ConfigStoreCachedMixin
from configfactory.services.configsettings import get_environment_settings
from configfactory.services.environments import (
    get_user_or_group_view_environments,
)
from configfactory.utils import dicthelper


class APIView(BaseAPIView):

    request: Request = None

    authentication_classes = (TokenAuthentication,)

    permission_classes = (IsAuthenticated,)

    @cached_property
    def environments(self):
        return get_user_or_group_view_environments(user_or_group=self.request.user)


class EnvironmentsAPIView(APIView):

    def get(self, request):
        serializer = EnvironmentSerializer(
            instance=self.environments,
            many=True,
            context={
                'request': request
            },
        )
        return Response(serializer.data)


class SettingsAPIView(ConfigStoreCachedMixin, APIView):

    renderer_classes = (
        JSONRenderer,
        DotEnvRenderer,
    )

    def get(self, request, environment: str, **kwargs):
        environment = get_object_or_404(self.environments, alias=environment)
        data = dicthelper.flatten(get_environment_settings(environment))
        return Response(data)
