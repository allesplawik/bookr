from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from book.serializers import (
    PublisherSerializer,
    BookSerializerOnlyView
)
from rest_framework import status
from core.models import (
    Book,
    Publisher,
    Review
)

import pendulum


def book_create(user, **params):
    defaults = {
        'title': 'Book Title',
        'publication_date': '2023-01-01',
        'isbn': '123456789',
    }
    defaults.update(params)

    return Book.objects.create(user=user, **defaults)


def create_user(**params):
    defaults = {
        'email': 'user@example.com',
        'name': 'User',
        'password': 'userpass123'
    }

    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def create_review(user, **params):
    defaults = {
        'title': 'First review',
        'content': 'The best book',
        'rating': 10
    }

    defaults.update(params)
    return Review.objects.create(user=user, **defaults)


BOOK_URL = reverse('book:book-list')


def review_detail_url(book_id):
    return reverse('book:book-review-manage', args=(book_id,))


def detail_url(book_id):
    return reverse('book:book-detail', args=[book_id])


class PublicBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_book_list_unauthenticated(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retreive_books(self):
        other_user = create_user(
            email='user@example.com',
            name='User',
            password='testpass123'
        )
        book_create(user=self.user, title='Book1')
        book_create(user=self.user, title='Book2')
        book_create(user=other_user, title='Book3')

        res = self.client.get(BOOK_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        books = Book.objects.all().order_by('-id')
        serializer = BookSerializerOnlyView(books, many=True)

        self.assertEqual(serializer.data, res.data)

    def test_books_patch_not_allowed(self):
        """Testing that books not accept partial updates."""
        payload = {}

        res = self.client.patch(BOOK_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_books_put_not_allowed(self):
        """Testing that books not accept full update."""
        payload = {}

        res = self.client.put(BOOK_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_book(self):
        payload = {
            'title': 'Book Title',
            'publication_date': '2023-01-01',
            'isbn': '123456789'
        }

        res = self.client.post(BOOK_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(user=self.user)

        self.assertEqual(str(book), book.title)
        self.assertEqual(book.user, self.user)

    def test_book_patial_update(self):
        isbn_origin = '1111111'
        book = book_create(user=self.user, isbn=isbn_origin)

        payload = {
            'title': 'Book Updated',
            'publication_date': '2023-01-01'
        }
        publication_date_datetime = pendulum.date(2023, 1, 1)
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')
        book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.isbn, isbn_origin)
        self.assertEqual(book.publication_date, publication_date_datetime)
        self.assertEqual(book.user, self.user)

    def test_book_update_user(self):
        other_user = create_user(
            email='other_user@example.com',
            name='Other User',
        )

        book = book_create(user=self.user)
        payload = {
            'user': other_user.id
        }
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')
        book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.user, self.user)

    def test_book_full_update(self):
        book = book_create(user=self.user)

        payload = {
            'title': 'New title',
            'publication_date': '2023-07-07',
            'isbn': '22222222'
        }
        publication_date_datetime = pendulum.date(2023, 7, 7)
        url = detail_url(book.id)
        res = self.client.put(url, payload, format='json')
        book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.user, self.user)
        self.assertEqual(book.title, payload['title'])
        self.assertEqual(book.publication_date, publication_date_datetime)
        self.assertEqual(book.isbn, payload['isbn'])

    def test_book_update_only_for_owner(self):
        other_user = create_user(
            email='user@example.com',
            name='User',
            password='testpass123'
        )
        book = book_create(user=other_user)
        payload = {}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_delete_only_for_owner(self):
        other_user = create_user(
            email='user@example.com',
            name='User',
            password='testpass123'
        )
        book = book_create(user=other_user)
        url = detail_url(book.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


PUBLISHER_URL = reverse('book:publisher-list')


def create_publisher(user, **params):
    defaults = {
        'name': 'Test Publisher',
        'website': 'http://test.publisher.com',
        'email': 'test.publisher@example.com',
    }

    defaults.update(params)
    return Publisher.objects.create(user=user, **defaults)


def detail_publisher_url(publisher_id):
    return reverse('book:publisher-detail', args=[publisher_id])


class PublisherApiView(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_create_publisher(self):
        payload = {
            'name': 'Test Publisher',
            'website': 'http://example.com/publisher',
            'email': 'test.publoisher@example.com'
        }

        res = self.client.post(PUBLISHER_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        publisher = Publisher.objects.get(name=payload['name'])
        self.assertEqual(str(publisher), payload['name'])
        self.assertEqual(publisher.email, payload['email'])
        self.assertEqual(publisher.website, payload['website'])

    def test_retrieve_publishers(self):
        create_publisher(user=self.user)
        create_publisher(user=self.user)

        res = self.client.get(PUBLISHER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        publishers = Publisher.objects.filter(user=self.user).order_by('-id')
        serializer = PublisherSerializer(publishers, many=True)

        self.assertEqual(serializer.data, res.data)

    def test_retrieve_publishers_limited(self):
        other_user = create_user(
            email='other@example.com',
            name='Other user',
            password='testpass123'
        )
        p1 = create_publisher(
            name='Publisher1',
            user=other_user
        )
        p2 = create_publisher(
            name='Publisher2',
            user=self.user
        )
        p3 = create_publisher(
            name='Publisher3',
            user=self.user
        )
        res = self.client.get(PUBLISHER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        s1 = PublisherSerializer(p1)
        s2 = PublisherSerializer(p2)
        s3 = PublisherSerializer(p3)

        self.assertNotIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertIn(s3.data, res.data)

    def test_publisher_partial_update(self):
        origin_email = 'publisher@example.com'
        publisher = create_publisher(
            name='Publisher',
            user=self.user,
            email=origin_email
        )
        url = detail_publisher_url(publisher.id)
        payload = {
            'website': 'https://updsted.com/publisher'
        }
        res = self.client.patch(url, payload, format='json')
        publisher.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(publisher.website, payload['website'])
        self.assertEqual(publisher.email, origin_email)

    def test_full_update(self):
        publisher = create_publisher(user=self.user)
        url = detail_publisher_url(publisher.id)
        payload = {
            'name': 'Publisher Updated',
            'website': 'https://updsted.com/publisher',
            'email': 'updated@example.com'
        }
        res = self.client.put(url, payload, format='json')
        publisher.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(str(publisher), publisher.name)
        self.assertEqual(publisher.website, payload['website'])
        self.assertEqual(publisher.email, payload['email'])
        self.assertEqual(publisher.user, self.user)

    def test_delete_publisher(self):
        publisher = create_publisher(user=self.user)
        url = detail_publisher_url(publisher.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        publisher_exists = Publisher.objects.filter(user=self.user).exists()
        self.assertFalse(publisher_exists)

    def test_create_book_with_publisher(self):
        payload = {
            'title': 'Book',
            'publication_date': '2023-08-08',
            'isbn': '1231231223',
            'publishers': [
                {
                    'name': 'Publisher1',
                    'website': 'https://example.com',
                    'email': 'publisher@example.com',
                }
            ]
        }
        res = self.client.post(BOOK_URL, payload, format='json')

        self.assertTrue(res.status_code, status.HTTP_201_CREATED)
        publisher = Publisher.objects.get(user=self.user)
        book = Book.objects.get(user=self.user)
        self.assertIn(publisher, book.publishers.all())

    def test_create_book_with_exsisting_publisher(self):
        publisher_details = {
            'name': 'Publisher',
            'website': 'https://example.com',
            'email': 'publisher@example.com',
        }
        publisher = create_publisher(user=self.user, **publisher_details)
        payload = {
            'title': 'Book',
            'publication_date': '2023-01-01',
            'isbn': '12312313',
            'publishers': [
                publisher_details
            ]
        }

        res = self.client.post(BOOK_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(user=self.user)
        self.assertEqual(book.publishers.count(), 1)
        self.assertIn(publisher, book.publishers.all())

    def test_update_book_publishers_add_new_one(self):
        publisher_details = {
            'name': 'Publisher',
            'website': 'https://example.com',
            'email': 'publisher@example.com',
        }
        publisher = Publisher.objects.create(user=self.user, **publisher_details)
        book = book_create(user=self.user)
        book.publishers.add(publisher)
        payload = {
            'publishers': [
                {
                    'name': 'New Publisher',
                    'website': 'https://new.example.com',
                    'email': 'new.publisher@example.com'
                }
            ]
        }
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')
        book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_publisher = Publisher.objects.get(name='New Publisher')
        self.assertNotIn(publisher, book.publishers.all())
        self.assertIn(new_publisher, book.publishers.all())

    def test_update_book_publisher_use_existing_publisher(self):
        publisher_details = {
            'name': 'Publisher',
            'website': 'https://example.com',
            'email': 'publisher@example.com',
        }
        publisher = Publisher.objects.create(user=self.user, **publisher_details)
        book = book_create(user=self.user)
        payload = {
            'title': 'Book',
            'publication_date': '2023-08-04',
            'isbn': '123123123',
            'publishers': [
                publisher_details
            ]
        }
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertIn(publisher, book.publishers.all())
        publishers = Publisher.objects.filter(user=self.user)
        self.assertEqual(publishers.count(), 1)

    def test_update_book_publishers_empty_list(self):
        book = book_create(user=self.user)

        payload = {
            'publishers': []
        }
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.publishers.count(), 0)

    def test_get_book_reviews(self):
        book = book_create(user=self.user)
        review = create_review(user=self.user)
        book.reviews.add(review)
        url = review_detail_url(book.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_review(self):
        book = book_create(user=self.user)
        payload = {
            'title': 'First review',
            'content': "The best book I've ever read.",
            'rating': 10
        }
        url = review_detail_url(book.id)
        res = self.client.post(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book.refresh_from_db()
        reviews = Review.objects.filter(user=self.user)
        review = reviews[0]
        self.assertIn(review, book.reviews.all())
