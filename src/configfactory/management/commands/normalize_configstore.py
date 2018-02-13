from django.core.management.base import BaseCommand

from configfactory import configstore


class Command(BaseCommand):

    help = 'Normalize Config Store.'

    def handle(self, *args, **options):

        configstore.normalize()
