from django.test import TestCase

from configfactory.test.factories import UserFactory


class AuthViewsTestCase(TestCase):

    def test_login(self):

        user = UserFactory()
        user.set_password('123123')
        user.save()

        response = self.client.get('/login/')

        self.assertEqual(response.status_code, 200)

        response = self.client.post('/login/', data={
            'username': user.username,
            'password': '123123'
        })

        self.assertRedirects(response, '/')

    def test_logout(self):

        user = UserFactory()

        self.client.force_login(user)

        response = self.client.get('/logout/')

        self.assertRedirects(response, '/login/')
