from django.utils.module_loading import autodiscover_modules

# Set public version
__version__ = '0.50'
__author__ = 'Anton Ruhlov <antonruhlov@gmail.com>'


def autodiscover():
    """
    Custom system autodiscover.
    """

    # Autodiscover signals subscribers
    autodiscover_modules('subscribers')


default_app_config = 'configfactory.apps.ConfigFactoryConfig'
