from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Book

User = get_user_model()

class BookAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "adminpass")
        self.user = User.objects.create_user("user", "user@example.com", "userpass")

        self.book = Book.objects.create(
            title="Book 1",
            author="Author 1",
            cover="HARD",
            inventory=5,
            daily_fee="2.99"
        )

    def test_list_books(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.book.title)

    def test_create_book_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/books/", {
            "title": "New Book",
            "author": "Author 2",
            "cover": "SOFT",
            "inventory": 10,
            "daily_fee": "1.50"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_create_book_as_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/books/", {
            "title": "New Book",
            "author": "Author 2",
            "cover": "SOFT",
            "inventory": 10,
            "daily_fee": "1.50"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 1)
