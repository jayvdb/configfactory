from django.test import TestCase

from configfactory.exceptions import (
    ComponentDeleteError,
    ComponentValidationError,
)
from configfactory.models import Config
from configfactory.services.components import (
    delete_component,
    get_settings,
    inject_params,
    update_component_settings,
    validate_component_settings,
)
from configfactory.test.factories import ComponentFactory, EnvironmentFactory


class ComponentsServiceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.base = EnvironmentFactory(
            name='Base',
            alias='base'
        )

    def test_nested_inject_components_data_params(self):

        names = ComponentFactory(
            name='Names',
            alias='names',
            is_global=True
        )

        hosts = ComponentFactory(
            name='Hosts',
            alias='hosts'
        )

        database = ComponentFactory(
            name='Database',
            alias='database'
        )

        development = EnvironmentFactory(
            name='Development',
            alias='development'
        )

        production = EnvironmentFactory(
            name='Production',
            alias='production'
        )

        update_component_settings(
            component=names,
            environment=self.base,
            settings={
                'db': 'mysql-base'
            }
        )

        update_component_settings(
            component=hosts,
            environment=self.base,
            settings={
                'db': '${param:names.db}'
            }
        )

        update_component_settings(
            component=hosts,
            environment=development,
            settings={
                'db': 'mysql-dev'
            }
        )

        prod_data = get_settings(
            component=hosts,
            environment=production,
        )

        prod_data = inject_params(production, prod_data)

        self.assertDictEqual(prod_data, {
            'db': 'mysql-base'
        })

        update_component_settings(
            component=database,
            environment=self.base,
            settings={
                'name': 'db',
                'host': '${param:hosts.db}',
                'port': 3567,
                'user': 'root',
                'pass': ''
            }
        )

        base_data = get_settings(
            component=database,
            environment=self.base,
        )

        base_data = inject_params(self.base, base_data)

        self.assertDictEqual(base_data, {
            'name': 'db',
            'host': 'mysql-base',
            'port': 3567,
            'user': 'root',
            'pass': '',
        })

        dev_data = get_settings(
            component=database,
            environment=development,
        )

        dev_data = inject_params(development, dev_data)

        self.assertDictEqual(dev_data, {
            'name': 'db',
            'host': 'mysql-dev',
            'port': 3567,
            'user': 'root',
            'pass': '',
        })

        prod_data = get_settings(
            component=database,
            environment=production,
        )

        prod_data = inject_params(production, prod_data)

        self.assertDictEqual(prod_data, {
            'name': 'db',
            'host': 'mysql-base',
            'port': 3567,
            'user': 'root',
            'pass': '',
        })

    def test_invalid_component_settings_key(self):

        database = ComponentFactory(
            name='Database',
            alias='database'
        )

        with self.assertRaises(ComponentValidationError) as exc:

            validate_component_settings(
                component=database,
                environment=self.base,
                settings={
                    'host': '${param:hosts.db}',
                    'port': 3567,
                    'user': 'root',
                    'password': '',
                    'database': ''
                }
            )

    def test_invalid_component_settings_referring_components(self):

        hosts = ComponentFactory(alias='hosts', name='Hosts')
        database = ComponentFactory(alias='database', name='Database')

        update_component_settings(
            component=hosts,
            environment=self.base,
            settings={
                'db': 'localhost'
            }
        )

        update_component_settings(
            component=database,
            environment=self.base,
            settings={
                'host': '${param:hosts.db}',
                'port': 3567,
                'user': 'root',
                'password': '',
                'database': ''
            }
        )

        with self.assertRaises(ComponentValidationError):
            validate_component_settings(
                component=hosts,
                environment=self.base,
                settings={
                    'db1': 'mysql-base'
                }
            )

    def test_invalid_json_schema(self):

        hosts = ComponentFactory(
            name='Hosts',
            alias='hosts'
        )

        database = ComponentFactory(
            name='Database',
            alias='database',
            require_schema=True,
        )
        database.schema = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'host': {
                    'type': 'string'
                },
                'port': {
                    'type': 'integer'
                },
                'user': {
                    'type': 'string'
                },
                'password': {
                    'type': 'string'
                },
                'database': {
                    'type': 'string'
                }
            },
            'required': [
                'host',
                'port',
                'user',
                'password',
                'database',
            ]
        }
        database.save()

        update_component_settings(
            component=hosts,
            environment=self.base,
            settings={
                'db': {
                    'host': 'mysql-db',
                    'port': '3567'
                }
            }
        )

        with self.assertRaises(ComponentValidationError):
            update_component_settings(
                component=database,
                environment=self.base,
                settings={
                    'host': '${param:hosts.db.host}',
                    'port': '${param:hosts.db.port}',
                    'user': 'root',
                    'password': '',
                    'database': ''
                }
            )

    def test_deny_add_environment_component_keys(self):

        development = EnvironmentFactory(
            name='Development',
            alias='development'
        )

        database = ComponentFactory(
            name='Database',
            alias='database',
            strict_keys=True,
        )

        update_component_settings(
            component=database,
            environment=self.base,
            settings={
                'host': 'localhost',
                'port': 3567,
            }
        )

        with self.assertRaises(ComponentValidationError):
            update_component_settings(
                component=database,
                environment=development,
                settings={
                    'host': 'mysql-dev',
                    'port': 3567,
                    'test': '123123'
                }
            )

    def test_deny_remove_environment_component_keys(self):

        development = EnvironmentFactory(
            name='Development',
            alias='development'
        )

        database = ComponentFactory(
            name='Database',
            alias='database',
            strict_keys=True,
        )

        update_component_settings(
            component=database,
            environment=self.base,
            settings={
                'host': 'localhost',
                'port': 3567,
            }
        )

        with self.assertRaises(ComponentValidationError):
            update_component_settings(
                component=database,
                environment=development,
                settings={
                    'host': 'mysql-dev',
                }
            )

    def test_deny_delete_referred_component(self):

        hosts = ComponentFactory(name='Hosts', alias='hosts')

        database = ComponentFactory(
            name='Database',
            alias='database'
        )

        update_component_settings(
            component=hosts,
            environment=self.base,
            settings={
                'db': 'localhost'
            }
        )

        update_component_settings(
            component=database,
            environment=self.base,
            settings={
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

        update_component_settings(
            component=hosts,
            environment=self.base,
            settings={
                'db': 'localhost'
            }
        )

        assert Config.objects.filter(environment=self.base.alias, component=hosts.alias).exists()

        delete_component(hosts)

        assert not Config.objects.filter(environment=self.base, component=hosts).exists()
