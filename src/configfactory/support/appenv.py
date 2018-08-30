import os
from distutils.util import strtobool

from configfactory.support import appdir

VAR_DEBUG = 'CONFIGFACTORY_DEBUG'
VAR_ENV = 'CONFIGFACTORY_ENV'
VAR_CONFIG = 'CONFIGFACTORY_CONFIG'

ENV_TESTING = 'testing'
ENV_DEVELOPMENT = 'development'
ENV_PRODUCTION = 'production'


def debug_enabled():
    return bool(strtobool(os.environ.get(VAR_DEBUG, 'no')))


def get_env() -> str:
    return os.environ[VAR_ENV]


def is_development() -> bool:
    return get_env() == ENV_DEVELOPMENT


def set_development_defaults():
    """
    Set development environment defaults.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configfactory.settings')
    os.environ.setdefault(VAR_DEBUG, 'yes')
    os.environ.setdefault(VAR_ENV, ENV_DEVELOPMENT)
    os.environ.setdefault(VAR_CONFIG, appdir.root_dir('configfactory.ini'))


def set_production_defaults():
    """
    Set development environment defaults.
    """
    default_config = appdir.root_dir('configfactory.ini')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configfactory.settings')
    os.environ.setdefault(VAR_DEBUG, 'no')
    os.environ.setdefault(VAR_ENV, ENV_PRODUCTION)
    os.environ.setdefault(VAR_CONFIG, default_config)
