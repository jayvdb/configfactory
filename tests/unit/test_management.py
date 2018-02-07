from django.test import TestCase

from configfactory.models import Environment


class ManagementTestCase(TestCase):

    def test_post_migrate_base_environment(self):

        environment = Environment.objects.base().get()

        assert environment.alias == 'base'

    def test_post_migrate_created_environments(self):

        assert Environment.objects.count() == 3

        development = Environment.objects.get(alias='development')

        assert development.name == 'Development'

        testing = Environment.objects.get(alias='testing')

        assert testing.name == 'Testing'
        assert testing.fallback == development
