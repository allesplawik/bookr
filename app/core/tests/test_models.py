"""Test models for application."""

from django.contrib.auth import get_user_model
from core.models import (
    Book,
    Publisher
)
from django.test import TestCase


def create_user(**params):
    defaults = {
        'email': 'test@example.com',
        'name': 'test',
        'password': 'test123'
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


class UserModelTest(TestCase):
    def test_user_create(self):
        user_details = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        user = get_user_model().objects.create_user(**user_details)
        self.assertEqual(str(user), user.email)
        self.assertEqual(user.name, user_details['name'])
        self.assertTrue(user.check_password(user_details['password']))

    def test_user_without_email_error(self):
        user_details = {
            'email': '',
            'password': 'testpass123',
            'name': 'Test User'
        }

        with self.assertRaises(ValueError):
            create_user(**user_details)

    def test_user_with_normalized_email(self):
        emails = [
            ['Test@Example.Com', 'Test@example.com'],
            ['TEST1@EXAMPLE.COM', 'TEST1@example.com'],
            ['test2@example.COM', 'test2@example.com'],
            ['test3@EXAMPLE.COM', 'test3@example.com'],
            ['tesT4@Example.COM', 'tesT4@example.com'],
        ]

        for email, expected in emails:
            user = create_user(
                email=email,
                name='Test User',
                password='testpass123'
            )

            self.assertEqual(str(user), expected)

    def test_create_superuser(self):
        user_details = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        user = get_user_model().objects.create_superuser(**user_details)

        self.assertEqual(str(user), user.email)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class BookTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()

    """Book model tests."""

    def test_create_book(self):
        """Testing create a new book."""
        book_details = {
            'title': 'Book Title',
            'publication_date': '2023-01-01',
            'isbn': '123456789',
            'user': self.user
        }
        book = Book.objects.create(**book_details)

        self.assertEqual(str(book), book.title)
        self.assertEqual(book.user, self.user)

    def test_book_create_with_publisher(self):
        p1 = create_publisher(name='Publisher1', user=self.user)
        p2 = create_publisher(name='Publisher2', user=self.user)
        book = Book.objects.create(
            title='Book',
            publication_date='2023-01-01',
            isbn='123456789',
            user=self.user,
        )
        book.publishers.add(p1, p2)
        self.assertIn(p1, book.publishers.all())
        self.assertIn(p2, book.publishers.all())


def create_publisher(user, **params):
    defaults = {
        'name': 'Test Publisher',
        'website': 'http://test.publisher.com',
        'email': 'test.publisher@example.com',
    }

    defaults.update(params)
    return Publisher.objects.create(user=user, **defaults)


class PublisherTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()

    def test_create_publisher(self):
        publisher = create_publisher(user=self.user)
        self.assertEqual(str(publisher), publisher.name)
        self.assertEqual(publisher.user, self.user)
