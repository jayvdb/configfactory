import pytest
from django.test import TestCase

from configfactory import configstore
from configfactory.exceptions import InvalidSettingsError
from configfactory.services.configsettings import (
    get_all_settings,
    get_environment_settings,
    get_settings,
    get_settings_inject_keys,
    inject_settings_params,
    update_settings,
    validate_settings,
)
from configfactory.test.factories import ComponentFactory, EnvironmentFactory


class ConfigSettingsServiceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        # Set environments
        cls.base = EnvironmentFactory(alias='base', name='Base')
        cls.dev = EnvironmentFactory(alias='dev', name='Development')
        cls.prod = EnvironmentFactory(alias='prod', name='Production')

        # Set components
        cls.hosts = ComponentFactory(alias='hosts', name='Hosts')
        cls.users = ComponentFactory(alias='users', name='Users')
        cls.credentials = ComponentFactory(alias='credentials', name='Credentials')
        cls.db = ComponentFactory(alias='db', name='Database')
        cls.redis = ComponentFactory(alias='redis', name='Redis')

    def test_get_all_settings(self):

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'user': 'root',
                'pass': ''
            }
        )

        update_settings(
            environment=self.dev,
            component=self.db,
            data={
                'user': 'devuser',
                'pass': '123123'
            }
        )

        data = get_all_settings()

        assert data == {
            'base': {
                'db': {
                    'user': 'root',
                    'pass': ''
                }
            },
            'dev': {
                'db': {
                    'user': 'devuser',
                    'pass': '123123'
                }
            }
        }

    def test_get_all_settings_cached(self):

        with self.assertNumQueries(3):
            get_all_settings()
            get_all_settings()
            get_all_settings()

        with self.assertNumQueries(1):
            with configstore.cached_data():
                get_all_settings()
                get_all_settings()
                get_all_settings()

    def test_get_env_settings(self):

        #########################
        # Base settings
        #########################
        update_settings(
            environment=self.base,
            component=self.hosts,
            data={
                'db': 'localhost:5671',
            }
        )

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'user': 'root',
                'pass': ''
            }
        )

        #########################
        # Dev settings
        #########################
        update_settings(
            environment=self.dev,
            component=self.hosts,
            data={
                'db': 'dev.hostname.com:5671',
            }
        )

        update_settings(
            environment=self.dev,
            component=self.db,
            data={
                'user': 'devuser',
                'pass': '123123'
            }
        )

        data = get_environment_settings(self.dev)

        assert data == {
            'users': {},
            'hosts': {
                'db': 'dev.hostname.com:5671',
            },
            'credentials': {},
            'redis': {},
            'db': {
                'user': 'devuser',
                'pass': '123123'
            },
        }

        data = get_environment_settings(self.dev, components=[self.hosts, self.db])

        assert data == {
            'hosts': {
                'db': 'dev.hostname.com:5671',
            },
            'db': {
                'user': 'devuser',
                'pass': '123123'
            }
        }

    def test_get_component_settings(self):

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'user': 'root',
                'pass': ''
            }
        )

        update_settings(
            environment=self.dev,
            component=self.db,
            data={
                'user': 'devuser',
                'pass': '123123'
            }
        )

        data = get_settings(environment=self.base, component=self.db)

        assert data == {
            'user': 'root',
            'pass': ''
        }

        data = get_settings(environment=self.dev, component=self.db)

        assert data == {
            'user': 'devuser',
            'pass': '123123'
        }

    def test_get_undefined_environment_settings(self):

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'user': 'root',
                'pass': ''
            }
        )

        data = get_settings(environment=self.dev, component=self.db)

        assert data == {
            'user': 'root',
            'pass': ''
        }

    def test_get_fallback_environment_settings(self):

        staging = EnvironmentFactory(alias='stag', name='Staging', fallback=self.dev)

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'host': 'localhost',
                'port': 3452
            }
        )

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'host': '10.10.11.11',
                'port': 3452
            }
        )

        data = get_settings(environment=staging, component=self.db)

        assert data == {
            'host': '10.10.11.11',
            'port': 3452
        }

    def test_get_missing_fallback_environment_settings(self):

        staging = EnvironmentFactory(alias='stag', name='Staging', fallback=self.dev)

        update_settings(
            environment=self.base,
            component=self.db, data={
                'host': 'localhost',
                'port': 3452
            }
        )

        data = get_settings(environment=staging, component=self.db)

        assert data == {
            'host': 'localhost',
            'port': 3452
        }

    def test_inject_settings_params(self):

        update_settings(
            environment=self.base,
            component=self.users,
            data={
                'db': 'admin'
            }
        )

        update_settings(
            environment=self.base,
            component=self.hosts,
            data={
                'db': 'test-db.hostname.com'
            }
        )

        update_settings(
            environment=self.base,
            component=self.credentials,
            data={
                'username': '${users.db}',
                'password': 'secret'
            }
        )

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'host': '${hosts.db}',
                'port': 3567,
                'user': '${credentials.username}',
                'pass': '${credentials.password}'
            }
        )

        data = inject_settings_params(
            environment=self.base,
            data=get_settings(environment=self.base, component=self.db)
        )

        assert data == {
            'host': 'test-db.hostname.com',
            'port': 3567,
            'user': 'admin',
            'pass': 'secret'
        }

    def test_get_inject_settings_keys(self):

        update_settings(
            environment=self.base,
            component=self.users,
            data={
                'db': 'admin'
            }
        )

        update_settings(
            environment=self.base,
            component=self.hosts,
            data={
                'db': 'test-db.hostname.com'
            }
        )

        update_settings(
            environment=self.base,
            component=self.credentials,
            data={
                'username': '${users.db}',
                'password': 'secret'
            }
        )

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'host': '${hosts.db}',
                'port': 3567,
                'user': '${credentials.username}',
                'pass': '${credentials.password}'
            }
        )

        inject_keys = get_settings_inject_keys(environment=self.base)

        assert inject_keys == {
            'credentials': {'users.db'},
            'db': {
                'hosts.db',
                'credentials.password',
                'credentials.username'
            }
        }

        inject_keys = get_settings_inject_keys(
            environment=self.base,
            component=self.db,
            data={
                'host': 'localhost',
                'port': 3567,
                'user': '${credentials.username}',
                'pass': '${credentials.password}'
            }
        )

        assert inject_keys == {
            'credentials': {'users.db'},
            'db': {
                'credentials.password',
                'credentials.username'
            }
        }

    def test_validate_settings_invalid_key(self):

        with pytest.raises(InvalidSettingsError) as exc_info:

            validate_settings(
                environment=self.base,
                component=self.db,
                data={
                    'host': '${hosts.db}',
                    'port': 3567,
                    'user': 'root',
                    'password': '',
                    'database': ''
                }
            )

        assert exc_info.value.message == 'Injected key `hosts.db` does not exist.'

    def test_validate_settings_invalid_key_reference(self):

        update_settings(
            environment=self.base,
            component=self.hosts,
            data={
                'db': 'localhost'
            }
        )

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'host': '${hosts.db}',
                'port': 3567,
                'user': 'root',
                'password': '',
                'database': ''
            }
        )

        with pytest.raises(InvalidSettingsError) as exc_info:
            validate_settings(
                environment=self.base,
                component=self.hosts,
                data={
                    'db1': 'mysql-base'
                }
            )

        assert exc_info.value.message == 'Component `db` refers to changed key `hosts.db`.'

    def test_validate_settings_invalid_json_schema(self):

        self.db.require_schema = True
        self.db.schema = {
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
        self.db.save()

        update_settings(
            environment=self.base,
            component=self.hosts,
            data={
                'db': {
                    'host': 'mysql-db',
                    'port': '3567'
                }
            }
        )

        with pytest.raises(InvalidSettingsError) as exc_info:
            validate_settings(
                environment=self.base,
                component=self.db,
                data={
                    'host': '${hosts.db.host}',
                    'port': '${hosts.db.port}',
                    'user': 'root',
                    'password': '',
                    'database': ''
                }
            )

        assert exc_info.value.message == 'Invalid settings schema: \'3567\' is not of type \'integer\'.'

    def test_validate_settings_invalid_add_key(self):

        self.db.require_schema = False
        self.db.strict_keys = True
        self.db.save()

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'host': 'localhost',
                'port': 3567,
            }
        )

        with pytest.raises(InvalidSettingsError) as exc_info:
            validate_settings(
                environment=self.dev,
                component=self.db,
                data={
                    'host': 'mysql-dev',
                    'port': 3567,
                    'test': '123123'
                }
            )

        assert exc_info.value.message == 'Cannot add new keys to environment configuration. New key(s): <b>test</b>.'

    def test_validate_settings_invalid_remove_key(self):

        self.db.require_schema = False
        self.db.strict_keys = True
        self.db.save()

        update_settings(
            environment=self.base,
            component=self.db,
            data={
                'host': 'localhost',
                'port': 3567,
            }
        )

        with pytest.raises(InvalidSettingsError) as exc_info:
            validate_settings(
                environment=self.dev,
                component=self.db,
                data={
                    'host': 'mysql-dev',
                }
            )

        assert exc_info.value.message == (
            'Cannot remove keys from environment configuration. Removed key(s): <b>port</b>.'
        )
