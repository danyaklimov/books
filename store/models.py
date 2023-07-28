from django.db import models
from django_filters.rest_framework import DjangoFilterBackend


class Book(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)

    def __str__(self):
        return f"ID: {self.id}, title: {self.title}"
