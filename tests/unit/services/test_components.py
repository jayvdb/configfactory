from django.test import TestCase

from configfactory.exceptions import ComponentDeleteError
from configfactory.models import Config
from configfactory.services.components import delete_component
from configfactory.services.configsettings import update_settings
from configfactory.test.factories import ComponentFactory, EnvironmentFactory


class ComponentsServiceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.base = EnvironmentFactory(name='Base', alias='base')

    def test_deny_delete_referred_component(self):

        hosts = ComponentFactory(name='Hosts', alias='hosts')

        database = ComponentFactory(
            name='Database',
            alias='database'
        )

        update_settings(
            environment=self.base,
            component=hosts,
            data={
                'db': 'localhost'
            }
        )

        update_settings(
            environment=self.base,
            component=database,
            data={
                'host': '${param:hosts.db}',
                'port': 3567,
                'user': 'root',
                'password': '',
                'database': ''
            }
        )

        with self.assertRaises(ComponentDeleteError):
            delete_component(hosts)

    def test_delete_component(self):

        hosts = ComponentFactory(name='Hosts', alias='hosts')

        update_settings(
            environment=self.base,
            component=hosts,
            data={
                'db': 'localhost'
            }
        )

        assert Config.objects.filter(environment=self.base.alias, component=hosts.alias).exists()

        delete_component(hosts)

        assert not Config.objects.filter(environment=self.base, component=hosts).exists()
