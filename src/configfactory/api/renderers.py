from rest_framework import renderers

from configfactory.utils import dotenv


class DotEnvRenderer(renderers.BaseRenderer):
    media_type = 'text/dotenv'
    format = 'env'

    def render(self, data, media_type=None, renderer_context=None):
        return dotenv.dumps(data)
