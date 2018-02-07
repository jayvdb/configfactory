import factory
import factory.django
from faker.utils.text import slugify


class EnvironmentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'configfactory.Environment'
        django_get_or_create = ('name', )

    @factory.lazy_attribute
    def alias(self):
        return slugify(self.name)
