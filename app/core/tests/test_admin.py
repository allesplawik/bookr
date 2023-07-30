from django.test import TestCase
from django.test import Client
from django.urls import reverse

from core.models import User


def create_superuser(**params):
    default = {
        'email': 'admint@example.com',
        'name': 'Admin User',
        'password': 'testpass123'
    }

    default.update(params)
    return User.objects.create_superuser(**default)


def create_user(**params):
    default = {
        'email': 'user@example.com',
        'name': 'User',
        'password': 'testpass123'
    }

    default.update(params)
    return User.objects.create_user(**default)


class UserAdminTest(TestCase):
    def setUp(self) -> None:
        self.admin = create_superuser()
        self.client = Client()
        self.client.force_login(self.admin)
        self.user = create_user()

    def test_list_users(self):
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_user_manage_page(self):
        url = reverse('admin:core_user_change', args=(self.user.id,))
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_user_add_page(self):
        url = reverse('admin:core_user_add')

        res = self.client.post(url)
        self.assertEqual(res.status_code, 200)
