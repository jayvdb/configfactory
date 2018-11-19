import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from configfactory.support import paths, env
from configfactory.support.config import config
from configfactory.support.logging import debug_logging

###########################################
# Main settings
###########################################
DEBUG = env.debug_enabled()

SECRET_KEY = config.get('secret_key', default='28$0ld^(u&7o%f_e4sqh@rl&lere4kzsca#@&6@f+#5k7r963b')

ROOT_URLCONF = 'configfactory.urls'

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ['127.0.0.1']

###########################################
# Database settings
###########################################
DATABASES = {
    'default': dj_database_url.config(
        env='CONFIGFACTORY_DATABASE_URI',
        default=config['database.url']
    )
}

###########################################
# Template settings
###########################################
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'configfactory.context_processors.components',
                'configfactory.context_processors.environments',
                'configfactory.context_processors.auth',
                'configfactory.context_processors.version',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        }
    },
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'configfactory.middleware.LoggingMiddleware',
    'configfactory.middleware.EnvironmentsMiddleware',
    'configfactory.middleware.ComponentsMiddleware',
    'configfactory.api.middleware.AccessMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INSTALLED_APPS = [

    'configfactory',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'crispy_forms',
    'guardian',
    'debug_toolbar',
]

######################################
# Static settings
######################################
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STATICFILES_DIRS = (
    paths.app_path('static'),
)

################################################################
# Media settings
################################################################
MEDIA_URL = '/media/'

MEDIA_ROOT = config.get('data_dir', default=paths.var_path('data'))

######################################
# Logging settings
######################################
LOGGING_DIR = config.get('logging.directory', paths.var_path('log'))

LOGGING_FILENAME = config.get('logging.filename', 'configfactory.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)-15s] (%(name)s) %(levelname)s - %(message)s",
        },
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s[%(asctime)-15s] (%(name)s) %(levelname)s - %(message)s",
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'colored'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(
                LOGGING_DIR,
                LOGGING_FILENAME
            ),
            'maxBytes': 5000000,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        # 'django': {
        #     'level': 'WARNING',
        #     'handlers': ['file'],
        # },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db': {
            'level': 'DEBUG',
            'handlers': [],
            'propagate': False,
        },
        'configfactory': {
            'level': 'DEBUG',
            'handlers': ['file'],
            'propagate': False,
        },
    }
}

if DEBUG:
    debug_logging(LOGGING, handler='console')

###########################################
# i10n / i18n settings
###########################################
LANGUAGE_CODE = 'en-US'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

###########################################
# Cache settings
###########################################
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}

###########################################
# Auth / users settings
###########################################
DEFAULT_USERS = [
    {
        'username': 'admin',
        'password': 'admin',
        'is_superuser': True,
    },
    {
        'username': 'guest',
        'password': 'guest',
    }
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'configfactory.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend'
)

ANONYMOUS_USER_NAME = None

LOGIN_URL = 'login'

LOGIN_REDIRECT_URL = 'dashboard'

###########################################
# Crispy forms settings
###########################################
CRISPY_TEMPLATE_PACK = 'bootstrap3'

###########################################
# ConfigFactory settings
###########################################
DEFAULT_ENVIRONMENTS = [
    {
        'name': 'Development',
        'alias': 'development'
    }
]

BASE_ENVIRONMENT = 'base'

# Data encryption
ENCRYPT_ENABLED = config.get('encrypt.enabled', default=False)

ENCRYPT_TOKEN = config.get('encrypt.token', default=SECRET_KEY)

ENCRYPT_PREFIX = '$$$ENCRYPTED$$$:'

# Check encrypt key length
if ENCRYPT_ENABLED:
    if not ENCRYPT_TOKEN or len(ENCRYPT_TOKEN) < 32:
        raise ImproperlyConfigured('Encrypt key must set and greater or equal to 32 symbols.')

# Secured keys
SECURE_KEYS = config.getlist('secure_keys', default=['pass', 'password'])

# ConfigStore settings
CONFIGSTORE_BACKEND = config.get('configstore.backend', default='database')

CONFIGSTORE_OPTIONS = config.getdict('configstore.options.', default={})

# Backups settings
BACKUPS_INTERVAL = config.getint('backup.interval', default=7200)  # Every 2 hours

BACKUPS_CLEAN_INTERVAL = config.getint('backup.clean_interval', default=21600)  # Every 6 hours

BACKUPS_CLEAN_THRESHOLD = config.getint('backup.clean_threshold', default=168)  # Every week
