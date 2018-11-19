from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import (
    TokenAuthentication as BaseTokenAuthentication,
)

from configfactory.models import APISettings, User


class TokenAuthentication(BaseTokenAuthentication):

    def authenticate_credentials(self, key):

        api_settings: APISettings = (
            APISettings
            .objects
            .active()
            .filter(token=key)
            .first()
        )

        if not api_settings:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if isinstance(api_settings.user_or_group, User) and not api_settings.user_or_group.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return api_settings.user_or_group, None
