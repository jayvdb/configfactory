from django.core.management.base import BaseCommand

from configfactory.services.configsettings import cleanup_settings


class Command(BaseCommand):

    help = 'Cleanup Config Store settings.'

    def handle(self, *args, **options):
        cleanup_settings()
