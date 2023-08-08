import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookAPITestCase(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create(username="test_user_1")
        self.book_1 = Book.objects.create(title="test book 1", price=25, author_name="Author 1",
                                          owner=self.test_user)
        self.book_2 = Book.objects.create(title="test book 2", price=40, author_name="Author 2")

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BookSerializer([self.book_1, self.book_2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 25})
        serializer_data = BookSerializer(self.book_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data[0])

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 2'})
        serializer_data = BookSerializer(self.book_2).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data[0])

    def test_get_order(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})
        serializer_data = BookSerializer([self.book_1, self.book_2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(2, Book.objects.all().count())
        self.client.force_login(self.test_user)
        url = reverse('book-list')
        data = {
            "title": "Book 4",
            "price": 135,
            "author_name": "Author 4"
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, Book.objects.all().count())
        self.assertEqual(Book.objects.last().owner, self.test_user)

    def test_update(self):
        self.client.force_login(self.test_user)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "title": self.book_1.title,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_update_not_owner(self):  ### негативный тест
        self.test_user_2 = User.objects.create(username="test_user_2")
        self.client.force_login(self.test_user_2)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "title": self.book_1.title,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(25, self.book_1.price)
        self.assertEqual(response.data, {'detail':
                                             ErrorDetail(string='You do not have permission to perform this action.',
                                                         code='permission_denied')})

    def test_update_not_owner_but_staff(self):
        self.test_user_2 = User.objects.create(username="test_user_2", is_staff=True)
        self.client.force_login(self.test_user_2)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "title": self.book_1.title,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_delete(self):
        self.assertEqual(2, Book.objects.all().count())
        self.client.force_login(self.test_user)
        url = reverse('book-detail', args=(self.book_1.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(1, Book.objects.all().count())

    def test_get_id(self):
        url = reverse('book-detail', args=(self.book_2.id,))
        response = self.client.get(url)
        serializer_data = BookSerializer(self.book_2).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

class BookRelationAPITestCase(APITestCase):
    def setUp(self):
        self.test_user_1 = User.objects.create(username="test_user_1")
        self.test_user_2 = User.objects.create(username="test_user_2")
        self.book_1 = Book.objects.create(title="test book 1", price=25, author_name="Author 1",
                                          owner=self.test_user_1)
        self.book_2 = Book.objects.create(title="test book 2", price=40, author_name="Author 2")

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_2.id,))
        data = {
            'like': True
        }
        json_data = json.dumps(data)
        self.client.force_login(self.test_user_1)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.test_user_1, book=self.book_2)
        self.assertTrue(relation.like)

        data = {
            'in_bookmarks': True
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.test_user_1, book=self.book_2)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_2.id,))
        data = {
            'rate': 3
        }
        json_data = json.dumps(data)
        self.client.force_login(self.test_user_1)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.test_user_1, book=self.book_2)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_2.id,))
        data = {
            'rate': 6
        }
        json_data = json.dumps(data)
        self.client.force_login(self.test_user_1)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        print(response.data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        relation = UserBookRelation.objects.get(user=self.test_user_1, book=self.book_2)
        self.assertEqual(response.data, {'rate': [ErrorDetail(string='"6" is not a valid choice.', code='invalid_choice')]})