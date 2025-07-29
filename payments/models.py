from django.db import models
from django.conf import settings

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    borrowing = models.ForeignKey(
        "borrowings.Borrowing",
        on_delete=models.CASCADE,
        related_name="payments"
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
