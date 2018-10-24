import logging

from django.utils.functional import SimpleLazyObject

from configfactory.services.components import get_user_components
from configfactory.services.environments import (
    get_user_change_environments,
    get_user_view_environments,
)
from configfactory.utils import json
from configfactory.utils.http import get_client_ip

logger = logging.getLogger(__name__)


class EnvironmentsMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.view_environments = SimpleLazyObject(
            lambda: get_user_view_environments(request.user)
        )
        request.change_environments = SimpleLazyObject(
            lambda: get_user_change_environments(request.user)
        )
        return self.get_response(request)


class ComponentsMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.components = SimpleLazyObject(
            lambda: get_user_components(request.user)
        )
        return self.get_response(request)


class LoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info('[{ip_address}] {method} {path}: {params}'.format(
            ip_address=get_client_ip(request),
            method=request.method.upper(),
            path=request.path,
            params=json.dumps(
                obj=request.GET if request.method == 'GET' else request.POST
            ),
        ))
        return self.get_response(request)
