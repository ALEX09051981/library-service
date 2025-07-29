from datetime import date

from django.conf import settings
from django.db import models
from books.models import Book


class Borrowing(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    @property
    def is_active(self):
        return self.actual_return_date is None

    def get_borrowing_days(self):
        end_date = self.actual_return_date or date.today()
        delta = (end_date - self.borrow_date).days
        return max(delta, 1)

    def __str__(self):
        return f"{self.user} borrowed {self.book}"
