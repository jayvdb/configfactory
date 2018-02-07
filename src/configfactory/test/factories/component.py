import factory.django


class ComponentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'configfactory.Component'
        django_get_or_create = ('name', )
