from celery import shared_task
from .bot import TelegramBot

@shared_task
def send_telegram_notification(chat_id, message):

    bot = TelegramBot()
    bot.send_message(chat_id, message)
