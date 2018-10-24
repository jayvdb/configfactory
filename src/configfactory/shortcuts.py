from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import NoReverseMatch


def get_base_environment() -> str:
    return settings.BASE_ENVIRONMENT


def is_base_environment(environment: str) -> bool:
    return get_base_environment() == environment


def back_url(to, request=None, query_param='next', *args, **kwargs) -> str:
    try:
        default_url = resolve_url(to, *args, **kwargs)
    except NoReverseMatch:
        default_url = None
    if request:
        return request.GET.get(query_param, default_url)
    return default_url
