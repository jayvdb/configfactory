import factory.django

from configfactory.models import Component, Environment


class ConfigFactory(factory.django.DjangoModelFactory):

    settings = {}

    class Meta:
        model = 'configfactory.Config'
        django_get_or_create = ('environment', 'component')

    @factory.lazy_attribute
    def environment(self) -> str:
        _environment = factory.SubFactory('configfactory.test.factories.EnvironmentFactory')  # type: Environment
        return _environment.alias

    @factory.lazy_attribute
    def component(self) -> str:
        _component = factory.SubFactory('configfactory.test.factories.ComponentFactory')  # type: Component
        return _component.alias
