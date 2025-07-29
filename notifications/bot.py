import requests
from django.conf import settings


class TelegramBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, chat_id: int, text: str):
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(self.api_url, data=data)
        return response.json()
