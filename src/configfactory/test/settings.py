from configfactory.settings import *

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
