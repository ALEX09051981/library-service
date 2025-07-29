from django.test import TestCase
from unittest.mock import patch, MagicMock
from notifications.tasks import send_telegram_notification


class SendTelegramNotificationTest(TestCase):
    @patch("notifications.tasks.requests.post")
    def test_send_telegram_notification_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = send_telegram_notification(623504868, "Test message")

        mock_post.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    @patch("notifications.tasks.requests.post")
    def test_send_telegram_notification_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        result = send_telegram_notification(623504868, "Bad request")

        mock_post.assert_called_once()
        self.assertEqual(result, {"status": "error", "code": 400})
