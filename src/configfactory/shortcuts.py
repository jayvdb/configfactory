from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import NoReverseMatch


def get_base_environment_alias():
    return settings.BASE_ENVIRONMENT


def back_url(to, request=None, *args, **kwargs):
    try:
        default_url = resolve_url(to, *args, **kwargs)
    except NoReverseMatch:
        default_url = None
    if request:
        return request.GET.get('next', default_url)
    return default_url
