import pytest

from configfactory.models import Environment
from configfactory.test.factories import EnvironmentFactory


@pytest.mark.django_db
def test_environment_order():

    Environment.objects.non_base().delete()

    first = EnvironmentFactory(name='First')

    assert first.order == 0

    second = EnvironmentFactory(name='Second')

    assert second.order == 1

    third = EnvironmentFactory(name='Third', order=5)

    assert third.order == 5

    fourth = EnvironmentFactory(name='Fourth')

    assert fourth.order == 6
