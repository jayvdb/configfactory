import os
from distutils.util import strtobool

from configfactory.support import dirs


def debug_enabled():
    return bool(strtobool(os.environ.get('CONFIGFACTORY_DEBUG', 'no')))


def set_defaults():
    """
    Set application default environment variables.
    """
    default_config = dirs.root_dir('configfactory.ini')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configfactory.settings')
    os.environ.setdefault('CONFIGFACTORY_DEBUG', 'no')
    os.environ.setdefault('CONFIGFACTORY_CONFIG', default_config)
