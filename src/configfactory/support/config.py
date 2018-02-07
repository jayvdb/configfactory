import logging
import os
import shutil

import appdirs
import yaml
from django.utils.functional import LazyObject

from configfactory.utils import dicthelper

logger = logging.getLogger(__name__)


class Config:

    envvar = 'CONFIGFACTORY_CONFIG'

    target_filename = 'configfactory.yml'

    default_filename = os.path.join(os.path.dirname(__file__), 'defaults.yml')

    def __init__(self):
        self._settings = {}
        self.is_default = False

    def default(self):
        return os.environ.get(
            self.envvar,
            appdirs.user_data_dir(self.target_filename)
        )

    def load(self):
        config_file = os.environ.get(
            self.envvar,
            appdirs.user_data_dir(self.target_filename)
        )
        if not os.path.exists(config_file):
            logger.warning('Configuration file `{}` does not exists. Using defaults.'.format(config_file))
            self.is_default = True
            config_file = self.default_filename
        self._settings = dicthelper.flatten(
            yaml.load(open(config_file))
        )

    def create(self, dst=None, overwrite=False):

        if dst is None:
            dst = os.environ.get(
                self.envvar,
                appdirs.user_data_dir(self.target_filename)
            )

        if os.path.exists(dst) and not overwrite:
            return dst, False

        shutil.copyfile(self.default_filename, dst)

        return dst, True

    def get(self, name, default=None, strict=False):
        if strict:
            return self._settings[name]
        return self._settings.get(name, default)

    def has(self, name):
        return name in self._settings

    def __getitem__(self, item):
        return self.get(item, strict=True)

    def __contains__(self, item):
        return self.has(item)


class ConfigHandler(LazyObject):

    def _setup(self):
        wrapped = Config()
        wrapped.load()
        self._wrapped = wrapped
