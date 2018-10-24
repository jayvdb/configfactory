import atexit
import shutil
import tempfile

# noinspection PyUnresolvedReferences
from configfactory.settings import *  # noqa

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

DATABASE_RENAME_TABLES = False

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
CONFIGSTORE_BACKEND = 'database'

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
