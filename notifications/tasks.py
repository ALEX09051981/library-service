import requests
from celery import shared_task
from django.conf import settings


@shared_task
def send_telegram_notification(chat_id: int, message: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return {"status": "success"}
    return {"status": "error", "code": response.status_code}
