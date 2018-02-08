import logging

from django.utils.functional import SimpleLazyObject

from configfactory.services.components import get_user_components
from configfactory.services.environments import get_user_environments
from configfactory.utils import json
from configfactory.utils.http import get_client_ip

logger = logging.getLogger(__name__)


def environments_middleware(get_response):
    """
    User environments middleware.
    """
    def middleware(request):
        request.view_environments = SimpleLazyObject(
            lambda: get_user_environments(request.user, perms=(
                'view_environment',
            ))
        )
        request.change_environments = SimpleLazyObject(
            lambda: get_user_environments(request.user, perms=(
                'change_environment',
            ))
        )
        response = get_response(request)
        return response
    return middleware


def components_middleware(get_response):
    """
    User components middleware.
    """
    def middleware(request):
        request.components = SimpleLazyObject(
            func=lambda: get_user_components(request.user)
        )
        response = get_response(request)
        return response
    return middleware


def logging_middleware(get_response):
    """
    Logging middleware.
    """
    def middleware(request):
        logger.info('[{ip_address}] {method} {path}: {params}'.format(
            ip_address=get_client_ip(request),
            method=request.method.upper(),
            path=request.path,
            params=json.dumps(
                obj=request.GET if request.method == 'GET' else request.POST
            ),
        ))
        response = get_response(request)
        return response
    return middleware
