import configparser
import logging
import os
import shutil
from distutils.util import strtobool
from typing import Any

import appdirs
from django.utils.functional import LazyObject, cached_property

from configfactory.support import paths

logger = logging.getLogger(__name__)


class Config:

    envvar = 'CONFIGFACTORY_CONFIG'

    target_filename = 'configfactory.ini'

    defaults_filename = os.path.join(os.path.dirname(__file__), 'defaults.ini')

    schema_filename = os.path.join(os.path.dirname(__file__), 'schema.json')

    def __init__(self):
        self._settings = {}
        self.is_default = False

    def __getitem__(self, item):
        return self.get(item, strict=True)

    @cached_property
    def config_file(self) -> str:

        env_or_user_data_path = os.environ.get(self.envvar, appdirs.user_data_dir(self.target_filename))
        if os.path.exists(env_or_user_data_path):
            return env_or_user_data_path

        project_path = paths.root_path(self.target_filename)
        if os.path.exists(project_path):
            return project_path

        if self.envvar in os.environ:
            logger.warning(f'Configuration file `{os.environ[self.envvar]}` does not exists. Using defaults.')

        self.is_default = True

        return self.defaults_filename

    def load(self):

        config = configparser.ConfigParser()

        with open(self.config_file) as fp:
            config.read_file(fp)

        for option in config.options('configfactory'):
            self._settings[option] = config.get('configfactory', option)

    def create(self, dst: str=None):

        if dst is None:
            dst = self.config_file

        if os.path.exists(dst):
            return dst, False

        shutil.copyfile(self.defaults_filename, dst)

        return dst, True

    def get(self, name, default=None, strict=False) -> Any:
        if strict:
            return self._settings[name]
        else:
            return self._settings.get(name, default)

    def getint(self, name, default=None, strict=False) -> int:
        return int(self.get(name, default=default, strict=strict))

    def getbool(self, name, default=None, strict=None) -> bool:
        value = self.get(name, default=default, strict=strict)
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        value = str(value).strip()
        return bool(strtobool(value))

    def getlist(self, name, default=None, strict=False) -> list:
        value = self.get(name, default=default, strict=strict)
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            value = filter(None, [x.strip() for x in value.splitlines()])
        values = list(value)
        result = []
        for value in values:
            subvals = value.split()
            result.extend(subvals)
        return result


class ConfigSetup(LazyObject):

    def _setup(self):
        config = Config()
        config.load()
        self._wrapped = config
