from django.test import TestCase

from configfactory.models import Component, Config, Environment
from configfactory.services.backups import create_backup, load_backup
from configfactory.services.configsettings import get_settings, update_settings
from configfactory.test.factories import ComponentFactory, EnvironmentFactory


class BackupsServiceTestCase(TestCase):

    def setUp(self):
        Environment.objects.all().delete()

    def test_create_and_load_backup(self):

        base = EnvironmentFactory(name='Base', alias='base')
        development = EnvironmentFactory(name='Development', alias='development')

        hosts = ComponentFactory(name='Hosts', alias='hosts')
        database = ComponentFactory(name='Database', alias='database')

        update_settings(environment=base, component=hosts, data={
            'a': '1',
            'b': '2',
            'c': '3',
        })

        update_settings(environment=development, component=hosts, data={
            'a': '1!',
            'b': '2!',
            'c': '3!',
        })

        update_settings(environment=base, component=database, data={
            'user': 'root',
            'pass': '',
            'host': 'mysql-base',
        })

        update_settings(environment=development, component=database, data={
            'user': 'admin',
            'pass': '123123',
            'host': 'mysql-dev',
        })

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

        base_hosts_data = get_settings(environment=base, component=hosts)

        assert base_hosts_data == {
            'a': '1',
            'b': '2',
            'c': '3',
        }

        development_hosts_data = get_settings(environment=development, component=hosts)

        assert development_hosts_data == {
            'a': '1!',
            'b': '2!',
            'c': '3!',
        }

        base_database_data = get_settings(environment=base, component=database)

        assert base_database_data == {
            'user': 'root',
            'pass': '',
            'host': 'mysql-base',
        }

        development_database_data = get_settings(environment=development, component=database)

        assert development_database_data == {
            'user': 'admin',
            'pass': '123123',
            'host': 'mysql-dev',
        }

    def test_fallback_environment(self):

        EnvironmentFactory(name='Base', alias='base', order=0)
        development = EnvironmentFactory(name='Development', alias='development', order=2)
        EnvironmentFactory(name='Testing', alias='testing', fallback=development, order=1)

        backup = create_backup(comment='Test')

        # Delete all
        Environment.objects.all().delete()

        load_backup(backup)

        assert Environment.objects.filter(alias='base').exists()
        assert Environment.objects.filter(alias='development').exists()
        assert Environment.objects.filter(alias='testing').exists()
