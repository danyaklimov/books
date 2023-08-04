from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from store.models import Book
from store.permissions import IsOwnerOrReadOnly
from store.serializers import BookSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price', 'author_name']
    search_fields = ['title', 'author_name']
    ordering_fields = ['price', 'author_name', 'title']
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):         # назначает owner'a при создании книги
        serializer.validated_data['owner'] = self.request.user
        serializer.save()

def auth(request):
    return render(request, 'oauth.html')
