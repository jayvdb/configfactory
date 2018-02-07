from django.contrib.auth.models import Group
from django.test import TestCase

from configfactory.test.factories import GroupFactory, UserFactory


class GroupsViewsTestCase(TestCase):

    def test_list_groups_non_superuser(self):

        user = UserFactory(is_superuser=False)

        self.client.force_login(user)

        response = self.client.get('/groups/')

        self.assertEqual(response.status_code, 403)

    def test_create_group_non_superuser(self):

        user = UserFactory(is_superuser=False)

        self.client.force_login(user)

        response = self.client.get('/groups/create/')

        self.assertEqual(response.status_code, 403)

    def test_list_groups(self):

        user = UserFactory(is_superuser=True)

        self.client.force_login(user)

        response = self.client.get('/groups/')

        self.assertEqual(response.status_code, 200)

    def test_create_group(self):

        self.assertEqual(Group.objects.count(), 0)

        user = UserFactory(is_superuser=True)

        self.client.force_login(user)

        response = self.client.get('/groups/create/')

        self.assertEqual(response.status_code, 200)

        response = self.client.post('/groups/create/', data={
            'name': 'Admin'
        })

        self.assertRedirects(response, '/groups/')

        self.assertTrue(Group.objects.filter(name='Admin').exists())

    def test_update_group(self):

        user = UserFactory(is_superuser=True)
        group = GroupFactory(name='Admin')

        self.client.force_login(user)

        response = self.client.get('/groups/{pk}/'.format(pk=group.pk))

        self.assertEqual(response.status_code, 200)

        response = self.client.post('/groups/{pk}/'.format(pk=group.pk), data={
            'name': 'API'
        })

        self.assertRedirects(response, '/groups/')

        group.refresh_from_db()

        self.assertEqual(group.name, 'API')

    def test_delete_group(self):

        user = UserFactory(is_superuser=True)
        group = GroupFactory(name='Admin')

        self.assertTrue(Group.objects.filter(name='Admin').exists())

        self.client.force_login(user)

        response = self.client.get('/groups/{pk}/delete/'.format(pk=group.pk))

        self.assertEqual(response.status_code, 200)

        response = self.client.post('/groups/{pk}/delete/'.format(pk=group.pk))

        self.assertRedirects(response, '/groups/')

        self.assertFalse(Group.objects.filter(name='Admin').exists())
