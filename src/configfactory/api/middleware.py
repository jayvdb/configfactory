from configfactory.api.utils import get_user_or_group

from django.http import HttpResponseForbidden


class AccessMiddleware:

    URL_PATH = '/api/'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if self._is_api(request):
            identity = get_user_or_group(request)
            if not identity:
                return HttpResponseForbidden()
            request.api_identity = identity

        return self.get_response(request)

    def _is_api(self, request) -> bool:
        return request.path.startswith(self.URL_PATH)
