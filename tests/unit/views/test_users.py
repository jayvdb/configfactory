from django.test import TestCase

from configfactory.models import User
from configfactory.test.factories import GroupFactory, UserFactory


class UsersViewsTestCase(TestCase):

    def test_list_users_non_superuser(self):

        user = UserFactory(is_superuser=False)

        self.client.force_login(user)

        response = self.client.get('/users/')

        self.assertEqual(response.status_code, 403)

    def test_create_user_non_superuser(self):

        user = UserFactory(is_superuser=False)

        self.client.force_login(user)

        response = self.client.get('/users/create/')

        assert response.status_code == 403

    def test_list_users(self):

        user = UserFactory(is_superuser=True)

        self.client.force_login(user)

        response = self.client.get('/users/')

        assert response.status_code == 200

    def test_create_user(self):

        self.client.force_login(UserFactory(is_superuser=True))

        response = self.client.get('/users/create/')

        self.assertEqual(response.status_code, 200)

        response = self.client.post('/users/create/', data={
            'username': 'test.user',
            'email': 'test.user@mail.com',
        })

        self.assertRedirects(response, '/users/')

        user = User.objects.get(username='test.user')

        assert user.email == 'test.user@mail.com'

    def test_update_user(self):

        user = UserFactory(username='test.user', email='test.user@mail.com')

        self.client.force_login(UserFactory(is_superuser=True))

        response = self.client.get('/users/{pk}/'.format(pk=user.pk))

        self.assertEqual(response.status_code, 200)

        response = self.client.post('/users/{pk}/'.format(pk=user.pk), data={
            'username': user.username,
            'email': 'real.user@mail.com',
        })

        self.assertRedirects(response, '/users/')

        user.refresh_from_db()

        self.assertEqual(user.email, 'real.user@mail.com')

    def test_update_user_access_groups(self):

        admin_group = GroupFactory(name='Admin')
        api_group = GroupFactory(name='API')

        user = UserFactory(username='test.user', email='test.user@mail.com')
        user.groups.add(api_group)
        user.save()

        self.client.force_login(UserFactory(is_superuser=True))

        response = self.client.get('/users/{pk}/'.format(pk=user.pk))

        self.assertEqual(response.status_code, 200)

        response = self.client.post('/users/{pk}/access/'.format(pk=user.pk), data={
            'groups': [admin_group.pk, api_group.pk]
        })

        self.assertRedirects(response, '/users/')
        self.assertEqual(user.groups.count(), 2)

    def test_delete_group(self):

        user = UserFactory(username='test.user')

        self.client.force_login(UserFactory(is_superuser=True))

        response = self.client.get('/users/{pk}/delete/'.format(pk=user.pk))

        assert response.status_code == 200

        response = self.client.post('/users/{pk}/delete/'.format(pk=user.pk))

        self.assertRedirects(response, '/users/')

        assert not User.objects.filter(username='test.user').exists()
