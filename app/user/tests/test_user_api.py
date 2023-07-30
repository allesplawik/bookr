from rest_framework.test import APIClient
from rest_framework import status

from django.test import TestCase
from django.urls import reverse

from core.models import User

from user.serializers import UserSerializer


def create_user(**params):
    defaults = {
        'email': 'test@example.com',
        'name': 'Test User',
        'password': 'testpass123'
    }

    defaults.update(params)
    return User.objects.create_user(**defaults)


CREATE_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


class PublicUserApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user(self):
        payload = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpass123'
        }

        res = self.client.post(CREATE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=payload['email'])
        self.assertEqual(str(user), payload['email'])
        self.assertTrue(user.check_password(payload['password']))

    def test_create_user_with_existing_emai(self):
        create_user(
            email='user@example.com'
        )
        payload = {
            'email': 'user@example.com',
            'name': 'User',
            'password': 'testpass123'
        }

        res = self.client.post(CREATE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_token(self):
        create_user(
            email='user@example.com',
            password='testpass123'
        )
        payload = {
            'email': 'user@example.com',
            'password': 'testpass123'
        }

        res = self.client.post(TOKEN_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_with_bad_credentials(self):
        create_user(
            email='user@example.com',
            password='testpass123'
        )
        payload = {
            'email': 'user@example.com',
            'password': 'wrongpassword'
        }

        res = self.client.post(TOKEN_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_with_blank_password(self):
        create_user(
            email='user@example.com',
            password='testpass123'
        )
        payload = {
            'email': 'user@example.com',
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_unauthenticated(self):

        payload = {}
        res = self.client.post(TOKEN_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)


class PrivateUserApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_me(self):

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user = User.objects.get(email=self.user.email)
        serializer = UserSerializer(user)

        self.assertEqual(serializer.data, res.data)

    def test_me_partial_update(self):

        payload = {
            'name': 'User updated'
        }

        res = self.client.patch(ME_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])

    def test_full_update(self):

        payload = {
            'email': 'test_updsted@example.com',
            'name': 'User updated',
            'password': 'password updated'
        }

        res = self.client.put(ME_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))

    def test_me_post_not_allowed(self):

        payload = {}

        res = self.client.post(ME_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
