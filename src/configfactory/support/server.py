import gunicorn.app.base
from dj_static import Cling
from django.core.wsgi import get_wsgi_application

from configfactory.support import dirs


class ConfigFactoryServer(gunicorn.app.base.BaseApplication):
    """
    Gunicorn WSGI server.
    """

    def __init__(self, options=None):
        self.wsgi_application = get_wsgi_application()
        self.options = options or {}
        super().__init__()

    def init(self, parser, opts, args):
        pass

    def load_config(self):
        config = dict(
            [
                (key, value)
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            ]
        )
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return Cling(
            application=self.wsgi_application,
            base_dir=dirs.package_dir('static')
        )
