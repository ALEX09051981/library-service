from django.http import JsonResponse

def payment_success(request):
    return JsonResponse({"message": "Payment successful"})

def payment_cancel(request):
    return JsonResponse({"message": "Payment canceled"})
