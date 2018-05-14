# Set public version
__version__ = '0.54'
__author__ = 'Anton Ruhlov <antonruhlov@gmail.com>'


def autodiscover():
    """
    Custom system autodiscover.
    """

    from django.utils.module_loading import autodiscover_modules

    # Autodiscover signals subscribers
    autodiscover_modules('subscribers')


default_app_config = 'configfactory.apps.ConfigFactoryConfig'
