import pytest
from django.test import TestCase, override_settings

from configfactory import configstore
from configfactory.test.factories import ComponentFactory, EnvironmentFactory


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
        assert configstore.all() == {}

    def test_all_settings(self):

        configstore.update(self.base, self.db, data={
            'user': 'root',
            'pass': ''
        })

        configstore.update(self.dev, self.db, data={
            'user': 'devuser',
            'pass': '123123'
        })

        assert configstore.all() == {
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

        configstore.update(self.base, self.db, data={
            'user': 'user',
            'pass': 'secret'
        })

        configstore.update(self.base, self.redis, data={
            'url': 'redis://',
        })

        with self.assertNumQueries(3):
            configstore.all()
            configstore.all()
            configstore.all()

        with self.assertNumQueries(1):
            with configstore.cachecontext():
                configstore.all()
                configstore.all()
                configstore.all()

    def test_update_settings_invalid_type(self):

        with pytest.raises(TypeError):
            configstore.update(self.base, self.db, data=[1, 2, 3])

    def test_get_settings_base_environment(self):

        configstore.update(self.base, self.db, data={
            'name': 'mysql',
        })

        assert configstore.get(self.base, self.db) == {
            'name': 'mysql'
        }

    def test_get_settings_base_environment_empty_settings(self):

        assert configstore.get(self.base, self.db) == {}

    def test_get_settings_dev_environment(self):

        configstore.update(self.base, self.db, data={
            'name': 'mysql',
        })

        configstore.update(self.base, self.db, data={
            'name': 'mysql-dev',
        })

        assert configstore.get(self.dev, self.db) == {
            'name': 'mysql-dev'
        }

    def test_get_settings_dev_environment_not_defined(self):

        configstore.update(self.base, self.db, data={
            'name': 'mysql',
        })

        assert configstore.get(self.dev, self.db) == {
            'name': 'mysql'
        }

    def test_get_settings_dev_environment_missing(self):

        assert configstore.get(self.dev, self.db) == {}

    def test_get_settings_fallback_environment(self):

        staging = EnvironmentFactory(alias='stag', name='Staging', fallback=self.dev)

        configstore.update(self.base, self.db, data={
            'host': 'localhost',
            'port': 3452
        })

        configstore.update(self.dev, self.db, data={
            'host': '10.10.11.11',
            'port': 3452
        })

        assert configstore.get(staging, self.db) == {
            'host': '10.10.11.11',
            'port': 3452
        }

    def test_get_settings_fallback_environment_missing(self):

        staging = EnvironmentFactory(alias='stag', name='Staging', fallback=self.dev)

        configstore.update(self.base, self.db, data={
            'host': 'localhost',
            'port': 3452
        })

        assert configstore.get(staging, self.db) == {
            'host': 'localhost',
            'port': 3452
        }

    def test_inject_params(self):

        configstore.update(self.base, self.names, data={
            'db': 'test-db'
        })

        configstore.update(self.base, self.credentials, data={
            'username': '${param:names.db}',
            'password': 'secret'
        })

        configstore.update(self.base, self.db, data={
            'host': 'localhost',
            'port': 3567,
            'user': '${param:credentials.username}',
            'pass': '${param:credentials.password}'
        })

        assert configstore.ikeys(self.base) == {
            'credentials': {'names.db'},
            'db': {
                'credentials.username',
                'credentials.password'
            },
        }

    def test_inject_params_empty_settings(self):
        assert configstore.ikeys(self.base, self.db) == {}
