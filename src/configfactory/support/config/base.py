import configparser
import logging
import os
import shutil

import appdirs
from django.utils.functional import LazyObject, cached_property

from configfactory.support import paths

logger = logging.getLogger(__name__)


class Config:

    envvar = 'CONFIGFACTORY_CONFIG'

    target_filename = 'configfactory.ini'

    defaults_filename = os.path.join(os.path.dirname(__file__), 'defaults.ini')

    schema_filename = os.path.join(os.path.dirname(__file__), 'schema.json')

    truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))
    falsey = frozenset(('f', 'false', 'n', 'no', 'off', '0'))

    def __init__(self):
        self._settings = {}
        self.is_default = False

    def __getitem__(self, item):
        return self.get(item, strict=True)

    def __contains__(self, item):
        return self.has(item)

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

    def has(self, name):
        return name in self._settings

    def get(self, name, default=None, strict=False, as_type=None):

        if strict:
            value = self._settings[name]
        else:
            value = self._settings.get(name, default)

        if as_type is list:
            return self._as_list(value)
        elif as_type is bool:
            return self._as_bool(value)
        elif as_type is int:
            return int(value)

        return value

    def getint(self, name, default=None, strict=None):
        return self.get(name, default=default, strict=strict, as_type=int)

    def getbool(self, name, default=None, strict=None):
        return self.get(name, default=default, strict=strict, as_type=bool)

    def getlist(self, name, default=None, strict=None):
        return self.get(name, default=default, strict=strict, as_type=list)

    def getdict(self, name: str, default: dict = None) -> dict:
        return self._as_dict(name) or default or {}

    def _as_bool(self, value) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        value = str(value).strip()
        return value.lower() in self.truthy

    def _as_list_cronly(self, value):
        if isinstance(value, str):
            value = filter(None, [x.strip() for x in value.splitlines()])
        return list(value)

    def _as_list(self, value, flatten=True) -> list:
        if isinstance(value, list):
            return value
        values = self._as_list_cronly(value)
        if not flatten:
            return values
        result = []
        for value in values:
            subvals = value.split()
            result.extend(subvals)
        return result

    def _as_dict(self, value) -> dict:
        if isinstance(value, dict):
            return value
        return {
            k.split(value, maxsplit=1)[-1]: v
            for k, v in self._settings.items() if k.startswith(value)
        }


class ConfigHandler(LazyObject):

    def _setup(self):
        config = Config()
        config.load()
        self._wrapped = config
