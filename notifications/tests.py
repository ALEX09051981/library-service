from django.test import TestCase
from unittest.mock import patch
from notifications.tasks import send_telegram_notification

class SendTelegramNotificationTest(TestCase):
    @patch("notifications.tasks.post")
    def test_send_telegram_notification_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"ok": True}

        chat_id = 123456
        text = "Test message"

        result = send_telegram_notification(chat_id, text)

        self.assertTrue(mock_post.called)
        called_url = mock_post.call_args[0][0]
        self.assertIn("sendMessage", called_url)
        payload = mock_post.call_args[1]["data"]
        self.assertEqual(payload["chat_id"], chat_id)
        self.assertEqual(payload["text"], text)
        self.assertEqual(result, {"ok": True})

    @patch("notifications.tasks.post")
    def test_send_telegram_notification_error(self, mock_post):
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {"ok": False}

        result = send_telegram_notification(123456, "Error")

        self.assertFalse(result["ok"])

