from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from books.models import Book
from borrowings.models import Borrowing

User = get_user_model()


class BorrowingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user1@example.com",
            password="pass123"
        )
        self.other_user = User.objects.create_user(
            email="user2@example.com",
            password="pass123"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="admin123"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=5,
            daily_fee=10,
            cover="HARD",
        )

        self.borrowing_url = reverse("borrowing-list")
        self.token_url = reverse("token_obtain_pair")

    def get_token(self, email, password):
        response = self.client.post(
            self.token_url,
            {"email": email, "password": password},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["access"]

    def authenticate(self, email, password):
        token = self.get_token(email, password)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

    def test_create_borrowing_decreases_inventory(self):
        self.authenticate("user1@example.com", "pass123")

        data = {
            "book": self.book.id,
            "expected_return_date": "2030-01-01"
        }
        response = self.client.post(self.borrowing_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)

    def test_return_borrowing_increases_inventory(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date="2030-01-01"
        )
        self.book.inventory = 4
        self.book.save()

        self.authenticate("user1@example.com", "pass123")

        url = reverse("borrowing-return-book", args=[borrowing.id])
        response = self.client.post(url, {"actual_return_date": "2030-01-10"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 5)

    def test_filter_is_active(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date="2030-01-01"
        )
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date="2030-01-01",
            actual_return_date="2030-01-05"
        )

        self.authenticate("user1@example.com", "pass123")

        response = self.client.get(self.borrowing_url + "?is_active=true")
        self.assertEqual(len(response.data), 1)

        response = self.client.get(self.borrowing_url + "?is_active=false")
        self.assertEqual(len(response.data), 1)

    def test_user_sees_only_own_borrowings(self):
        Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date="2030-01-01"
        )
        Borrowing.objects.create(
            user=self.other_user,
            book=self.book,
            expected_return_date="2030-01-01"
        )

        self.authenticate("user1@example.com", "pass123")

        response = self.client.get(self.borrowing_url)
        self.assertEqual(len(response.data), 1)
