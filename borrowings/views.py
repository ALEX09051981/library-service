import stripe
from django.conf import settings
from payments.models import Payment

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Borrowing
from .serializers import BorrowingSerializer, BorrowingReturnSerializer
from .permissions import IsOwnerOrAdmin


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("user", "book")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(
                actual_return_date__isnull=is_active.lower() == "true"
            )

        user_id = self.request.query_params.get("user_id")
        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]

        if book.inventory <= 0:
            raise ValueError("No books available to borrow.")

        book.inventory -= 1
        book.save()

        borrowing = serializer.save(user=self.request.user)

        # --- Stripe ---
        stripe.api_key = settings.STRIPE_SECRET_KEY
        amount = borrowing.book.daily_fee * borrowing.get_borrowing_days()

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Borrowing: {borrowing.book.title}"
                    },
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{settings.DOMAIN}/payments/success/",
            cancel_url=f"{settings.DOMAIN}/payments/cancel/",
        )

        Payment.objects.create(
            user=self.request.user,
            borrowing=borrowing,
            session_url=session.url,
            session_id=session.id,
            amount=amount
        )

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            return Response(
                {"detail": "Book already returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = BorrowingReturnSerializer(borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        book = borrowing.book
        book.inventory += 1
        book.save()

        return Response(BorrowingSerializer(borrowing).data)
