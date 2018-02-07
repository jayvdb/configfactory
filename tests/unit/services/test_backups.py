from django.test import TestCase

from configfactory.models import Component, Config, Environment
from configfactory.services.backups import create_backup, load_backup
from configfactory.services.components import (
    get_component_settings,
    update_component_settings,
)
from configfactory.test.factories import ComponentFactory, EnvironmentFactory


class BackupsServiceTestCase(TestCase):

    def test_create_and_load_backup(self):

        base = EnvironmentFactory(
            name='Base',
            alias='base'
        )

        development = EnvironmentFactory(
            name='Development',
            alias='development'
        )

        hosts = ComponentFactory(
            name='Hosts',
            alias='hosts'
        )

        database = ComponentFactory(
            name='Database',
            alias='database'
        )

        update_component_settings(
            component=hosts,
            environment=base,
            settings={
                'a': '1',
                'b': '2',
                'c': '3',
            }
        )

        update_component_settings(
            component=hosts,
            environment=development,
            settings={
                'a': '1!',
                'b': '2!',
                'c': '3!',
            }
        )

        update_component_settings(
            component=database,
            environment=base,
            settings={
                'user': 'root',
                'pass': '',
                'host': 'mysql-base',
            }
        )

        update_component_settings(
            component=database,
            environment=development,
            settings={
                'user': 'admin',
                'pass': '123123',
                'host': 'mysql-dev',
            }
        )

        backup = create_backup(comment='Test')

        # Delete all
        Environment.objects.all().delete()
        Component.objects.all().delete()
        Config.objects.all().delete()

        load_backup(backup)

        assert Environment.objects.filter(alias='base').exists()
        assert Environment.objects.filter(alias='development').exists()
        assert Component.objects.filter(alias='hosts').exists()
        assert Component.objects.filter(alias='database').exists()

        base_hosts_data = get_component_settings(hosts, environment=base)

        assert base_hosts_data == {
            'a': '1',
            'b': '2',
            'c': '3',
        }

        development_hosts_data = get_component_settings(hosts, environment=development)

        assert development_hosts_data == {
            'a': '1!',
            'b': '2!',
            'c': '3!',
        }

        base_database_data = get_component_settings(database, environment=base)

        assert base_database_data == {
            'user': 'root',
            'pass': '',
            'host': 'mysql-base',
        }

        development_database_data = get_component_settings(database, environment=development)

        assert development_database_data == {
            'user': 'admin',
            'pass': '123123',
            'host': 'mysql-dev',
        }
