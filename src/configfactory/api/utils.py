from typing import List, Optional, Union

from django.contrib.auth.models import Group

from configfactory.models import APISettings, User


def get_user_or_group(request) -> Optional[Union[User, Group]]:

    token: str = None
    auth: List[str] = request.META.get('HTTP_AUTHORIZATION', '').split()

    if len(auth) == 2 and auth[0].lower() == 'token':
        token = auth[1]

    if not token:
        return None

    api_settings: APISettings = (
        APISettings
        .objects
        .active()
        .filter(token=token)
        .first()
    )

    if api_settings:
        return api_settings.user_or_group

    return None
