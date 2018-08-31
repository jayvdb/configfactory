from django.http import HttpResponse

from configfactory.utils import dotenv


class DotEnvResponse(HttpResponse):

    def __init__(self, data: dict, **kwargs):
        data = dotenv.dumps(data)
        kwargs.setdefault('content_type', 'text/plain')
        super().__init__(content=data, **kwargs)
