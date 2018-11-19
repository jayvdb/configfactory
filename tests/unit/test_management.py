import pytest

from configfactory.models import Environment


@pytest.mark.django_db
def test_post_migrate_base_environment():

    environment = Environment.objects.base().get()

    assert environment.alias == 'base'


@pytest.mark.django_db
def test_post_migrate_created_environments():

    assert Environment.objects.count() == 3

    development = Environment.objects.get(alias='development')

    assert development.name == 'Development'

    testing = Environment.objects.get(alias='testing')

    assert testing.name == 'Testing'
    assert testing.fallback == development
