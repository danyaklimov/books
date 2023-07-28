import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BookAPITestCase(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create(username="test_user_1")
        self.book_1 = Book.objects.create(title="test book 1", price=25, author_name="Author 1")
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

    # def test_delete(self):
    #     self.assertEqual(2, Book.objects.all().count())
    #     self.client.force_login(self.test_user)
    #     url = reverse('book-detail', args=(self.book_1,))
    #     print(url)
    #     data = {
    #         "title": self.book_1.title,
    #         "price": self.book_1.price,
    #         "author_name": self.book_1.author_name
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.delete(url, data=json_data, content_type='applicataion/json')
    #     print(response)
    #     self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
    #     self.assertEqual(1, Book.objects.all().count())

    def test_get_id(self):
        url = reverse('book-detail', args=(self.book_2.id,))
        response = self.client.get(url)
        serializer_data = BookSerializer(self.book_2).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
