from rest_framework import serializers
from .models import Borrowing
from payments.models import Payment


class BorrowingSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()
    payment_url = serializers.SerializerMethodField()
    payment_amount = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = "__all__"
        read_only_fields = ("user", "borrow_date", "is_active")

    def get_payment_url(self, obj):
        payment = Payment.objects.filter(borrowing=obj).first()
        return payment.session_url if payment else None

    def get_payment_amount(self, obj):
        payment = Payment.objects.filter(borrowing=obj).first()
        return payment.amount if payment else None


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("actual_return_date",)
