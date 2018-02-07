import factory.django


class GroupFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'auth.Group'
        django_get_or_create = ('name', )
