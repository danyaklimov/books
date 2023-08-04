from unittest import TestCase

from store.models import Book
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(title="test book 1", price=25, author_name='author1')
        book_2 = Book.objects.create(title="test book 2", price=40, author_name='author2')
        data = BookSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'title': 'test book 1',
                'price': '25.00',
                'author_name': 'author1',
                'owner': None
            },
            {
                'id': book_2.id,
                'title': 'test book 2',
                'price': '40.00',
                'author_name': 'author2',
                'owner': None
            }
        ]
        self.assertEqual(expected_data, data)
