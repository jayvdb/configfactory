from collections import OrderedDict

from django.test import TestCase

from configfactory.models import Component
from configfactory.services.components import get_component_settings
from configfactory.test.factories import (
    ComponentFactory,
    EnvironmentFactory,
    UserFactory,
)


class ComponentsViewsTestCase(TestCase):

    def test_create_component(self):

        self.client.force_login(UserFactory(is_superuser=True))

        response = self.client.get('/components/create/')

        assert response.status_code == 200

        response = self.client.post('/components/create/', data={
            'name': 'Database',
            'alias': 'database',
            'is_global': False,
            'require_schema': False,
            'additional_prop': True
        })

        self.assertRedirects(response, '/components/database/', target_status_code=302)

        assert Component.objects.filter(alias='database').exists()

    def test_update_component(self):

        component = ComponentFactory(name='Database', alias='database')
        development = EnvironmentFactory(name='Development', alias='development')

        assert Component.objects.filter(alias='database').exists()

        self.client.force_login(UserFactory(is_superuser=True))

        response = self.client.get('/components/database/base/edit/')

        assert response.status_code == 200

        response = self.client.post('/components/database/base/edit/', data={
            'settings': """
            {
              "host": "localhost",
              "port": 3567,
              "user": "root",
              "password": null
            }
            """
        })

        self.assertRedirects(response, '/components/database/base/edit/')

        settings_dict = get_component_settings(component, environment=development)

        assert settings_dict == {
            'host': 'localhost',
            'port': 3567,
            'user': 'root',
            'password': None,
        }
