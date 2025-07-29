from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class PaymentIntegrationTest(APITestCase):
    def setUp(self):
        # Админ
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass"
        )

        # Обычный пользователь
        self.user = User.objects.create_user(
            email="user@example.com",
            password="userpass"
        )

        # Книга
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverType.SOFT,
            inventory=5,
            daily_fee=10.00
        )

    @patch("stripe.checkout.Session.create")
    def test_create_borrowing_creates_payment(self, mock_stripe_session_create):
        """Проверка, что при создании Borrowing создаётся Payment"""
        # Мокаем ответ Stripe
        mock_stripe_session_create.return_value = type(
            "obj", (object,), {
                "id": "sess_12345",
                "url": "https://stripe.com/checkout/sess_12345"
            }
        )

        self.client.force_authenticate(user=self.user)

        borrowing_data = {
            "book": self.book.id,
            "expected_return_date": "2025-08-05"
        }

        response = self.client.post("/api/borrowings/", borrowing_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что создано 1 платеж
        payment = Payment.objects.first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.borrowing.user, self.user)
        self.assertEqual(payment.session_id, "sess_12345")
        self.assertEqual(payment.session_url, "https://stripe.com/checkout/sess_12345")
        self.assertEqual(float(payment.amount), 10.00)  # daily_fee

        # Проверяем, что Stripe был вызван
        mock_stripe_session_create.assert_called_once()
