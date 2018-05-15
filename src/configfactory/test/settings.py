import atexit
import shutil
import tempfile

from configfactory.settings import *

TMP_ROOT = tempfile.mkdtemp(prefix='configfactory_')

tempfile.tempdir = TMP_ROOT
atexit.register(shutil.rmtree, str(TMP_ROOT))


###########################################
# Database settings
###########################################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

DATABASE_DB_TABLES_REPLACE = False

DATABASE_DB_TABLES_PREFIX = None

######################################
# Media settings
######################################
MEDIA_ROOT = TMP_ROOT

######################################
# Logging settings
######################################
LOGGING = None

######################################
# Security settings
######################################
ENCRYPT_ENABLED = False

###########################################
# Config store settings
###########################################
CONFIG_STORE = {
    'backend': 'database',
    'options': {}
}

######################################
# Environments settings
######################################
BASE_ENVIRONMENT = 'base'

DEFAULT_ENVIRONMENTS = [
    {
        'alias': 'development'
    },
    {
        'alias': 'testing',
        'fallback': 'development'
    }
]
