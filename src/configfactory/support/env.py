import os
from distutils.util import strtobool
from typing import Any

import dotenv

from configfactory.support import paths

VAR_DEBUG = 'APP_DEBUG'
VAR_ENV = 'APP_ENV'
VAR_CONFIG = 'APP_CONFIG'

ENV_LOCAL = 'local'
ENV_TESTING = 'testing'
ENV_PRODUCTION = 'production'


def get(varname: str, default: Any = None) -> Any:
    return os.getenv(varname, default)


def getbool(varname: str, default: bool = False) -> bool:
    return bool(strtobool(get(varname, str(default))))


def environment() -> str:
    return os.environ[VAR_ENV]


def is_local() -> bool:
    return environment() == ENV_LOCAL


def debug() -> bool:
    return bool(strtobool(os.environ.get(VAR_DEBUG, 'no')))


def setdefaults():

    # Define default environment variables
    os.environ.setdefault(VAR_ENV, ENV_LOCAL)
    os.environ.setdefault(VAR_DEBUG, 'yes')

    # Load DotEnv variables
    dotenv.load_dotenv(paths.root_path('.env.dist'))
    dotenv.load_dotenv(paths.root_path('.env'), override=True)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configfactory.settings')
    os.environ.setdefault(VAR_CONFIG, paths.root_path('configfactory.ini'))
