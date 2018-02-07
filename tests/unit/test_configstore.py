import pytest
from django.test import TestCase, override_settings

from configfactory import configstore
from configfactory.test.factories import ComponentFactory, EnvironmentFactory
from configfactory.test.factories.config import ConfigFactory


@override_settings(BASE_ENVIRONMENT='base')
class ConfigStoreTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        # Set environments
        cls.base = EnvironmentFactory(alias='base', name='Base')
        cls.dev = EnvironmentFactory(alias='dev', name='Development')
        cls.prod = EnvironmentFactory(alias='prod', name='Production')

        # Set components
        cls.db = ComponentFactory(alias='db', name='Database')
        cls.redis = ComponentFactory(alias='redis', name='Redis')
        cls.names = ComponentFactory(alias='names', name='Names')
        cls.credentials = ComponentFactory(alias='credentials', name='Credentials')

    def test_empty_store(self):
        assert configstore.all_settings() == {}

    def test_all_settings(self):

        ConfigFactory(environment=self.base, component=self.db, settings={
            'user': 'root',
            'pass': ''
        })

        ConfigFactory(environment=self.dev, component=self.db, settings={
            'user': 'devuser',
            'pass': '123123'
        })

        assert configstore.all_settings() == {
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

    def test_all_settings_cached(self):

        ConfigFactory(environment=self.base, component=self.db, settings={
            'user': 'user',
            'pass': 'secret'
        })

        ConfigFactory(environment=self.base, component=self.redis, settings={
            'url': 'redis://',
        })

        with self.assertNumQueries(3):
            configstore.all_settings()
            configstore.all_settings()
            configstore.all_settings()

        with self.assertNumQueries(1):
            with configstore.cachecontext():
                configstore.all_settings()
                configstore.all_settings()
                configstore.all_settings()

    def test_update_settings_invalid_type(self):

        with pytest.raises(TypeError):
            configstore.update_settings(self.base, self.db, [1, 2, 3])

    def test_get_settings_base_environment(self):

        configstore.update_settings(self.base, self.db, {
            'name': 'mysql',
        })

        assert configstore.get_settings(self.base, self.db) == {
            'name': 'mysql'
        }

    def test_get_settings_base_environment_empty_settings(self):

        assert configstore.get_settings(self.base, self.db) == {}

    def test_get_settings_dev_environment(self):

        configstore.update_settings(self.base, self.db, {
            'name': 'mysql',
        })

        configstore.update_settings(self.base, self.db, {
            'name': 'mysql-dev',
        })

        assert configstore.get_settings(self.dev, self.db) == {
            'name': 'mysql-dev'
        }

    def test_get_settings_dev_environment_not_defined(self):

        configstore.update_settings(self.base, self.db, {
            'name': 'mysql',
        })

        assert configstore.get_settings(self.dev, self.db) == {
            'name': 'mysql'
        }

    def test_get_settings_dev_environment_missing(self):

        assert configstore.get_settings(self.dev, self.db) == {}

    def test_get_settings_fallback_environment(self):

        staging = EnvironmentFactory(alias='stag', name='Staging', fallback=self.dev)

        configstore.update_settings(self.base, self.db, {
            'host': 'localhost',
            'port': 3452
        })

        configstore.update_settings(self.dev, self.db, {
            'host': '10.10.11.11',
            'port': 3452
        })

        assert configstore.get_settings(staging, self.db) == {
            'host': '10.10.11.11',
            'port': 3452
        }

    def test_get_settings_fallback_environment_missing(self):

        staging = EnvironmentFactory(alias='stag', name='Staging', fallback=self.dev)

        configstore.update_settings(self.base, self.db, {
            'host': 'localhost',
            'port': 3452
        })

        assert configstore.get_settings(staging, self.db) == {
            'host': 'localhost',
            'port': 3452
        }

    def test_inject_params(self):

        configstore.update_settings(self.base, self.names, {
            'db': 'test-db'
        })

        configstore.update_settings(self.base, self.credentials, {
            'username': '${param:names.db}',
            'password': 'secret'
        })

        configstore.update_settings(self.base, self.db, {
            'host': 'localhost',
            'port': 3567,
            'user': '${param:credentials.username}',
            'pass': '${param:credentials.password}'
        })

        assert configstore.inject_keys(self.base) == {
            'credentials': {'names.db'},
            'db': {
                'credentials.username',
                'credentials.password'
            },
        }

    def test_inject_params_empty_settings(self):
        assert configstore.inject_keys(self.base, self.db) == {}
