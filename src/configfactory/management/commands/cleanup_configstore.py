from django.core.management.base import BaseCommand

from configfactory import configstore
from configfactory.models import Component, Environment


class Command(BaseCommand):

    help = 'Cleanup Config Store.'

    def handle(self, *args, **options):

        for environment, components_data in configstore.all_settings().items():
            for component, settings in components_data.items():
                if not Environment.objects.filter(alias=environment).exists():
                    configstore.backend.delete_data(
                        environment=environment,
                        component=component
                    )
                    continue
                if not Component.objects.filter(alias=component).exists():
                    configstore.backend.delete_data(
                        environment=environment,
                        component=component
                    )
