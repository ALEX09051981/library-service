from django.db.models.signals import post_save
from django.dispatch import receiver
from borrowings.models import Borrowing
from payments.models import Payment
from tasks import send_telegram_notification


CHAT_ID = 623504868

@receiver(post_save, sender=Borrowing)
def notify_borrowing_created(sender, instance, created, **kwargs):
    if created:
        message = f"New loan created:\n{instance}"
        send_telegram_notification.delay(CHAT_ID, message)

@receiver(post_save, sender=Payment)
def notify_payment_success(sender, instance, created, **kwargs):
    if created and instance.status == 'success':
        message = f"Payment completed successfully:\n{instance}"
        send_telegram_notification.delay(CHAT_ID, message)
