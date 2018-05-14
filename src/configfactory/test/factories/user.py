import factory.django


class UserFactory(factory.django.DjangoModelFactory):

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    class Meta:
        model = 'configfactory.User'
        django_get_or_create = ('username', )

    @factory.lazy_attribute
    def username(self):
        return '{first_name}.{last_name}'.format(
            first_name=self.first_name,
            last_name=self.last_name
        ).lower()

    @factory.lazy_attribute
    def email(self):
        return '{username}@mail.com'.format(
            username=self.username,
        )
