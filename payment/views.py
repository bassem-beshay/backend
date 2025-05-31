from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions
from .models import Payment, PaymentMethod
from .serializers import PaymentSerializer, PaymentMethodSerializer
from orders.models import Order
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
import requests
import json


class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



#  Get authentication token
def get_paymob_token():
    url = "https://accept.paymob.com/api/auth/tokens"
    payload = { "api_key": settings.PAYMOB_API_KEY }
    res = requests.post(url, json=payload)
    return res.json()['token']

#  Create order on Paymob
def create_order(auth_token, amount_cents):
    url = "https://accept.paymob.com/api/ecommerce/orders"
    payload = {
        "auth_token": auth_token,
        "delivery_needed": False,
        "amount_cents": amount_cents,
        "currency": "EGP",
        "items": []
    }
    res = requests.post(url, json=payload)
    return res.json()['id']

# Generate payment key
def generate_payment_key(auth_token, amount_cents, order_id, phone_number):
    url = "https://accept.paymob.com/api/acceptance/payment_keys"
    payload = {
        "auth_token": auth_token,
        "amount_cents": amount_cents,
        "expiration": 3600,
        "order_id": order_id,
        "billing_data": {
            "apartment": "NA",
            "email": "customer@example.com",
            "floor": "NA",
            "first_name": "Bassem",
            "street": "NA",
            "building": "NA",
            "phone_number": phone_number,
            "shipping_method": "NA",
            "postal_code": "NA",
            "city": "Cairo",
            "country": "EG",
            "last_name": "Youssef",
            "state": "NA"
        },
        "currency": "EGP",
        "integration_id": settings.PAYMOB_INTEGRATION_ID_VF_CASH
    }
    res = requests.post(url, json=payload)
    return res.json()['token']

# Handle Payment Process (Vodafone Cash)
def pay_with_vodafone_cash(request):
    amount = 10000  
    phone = request.POST.get('phone_number')  

    
    token = get_paymob_token()

    
    paymob_order_id = create_order(token, amount)

  
    order = Order.objects.create(
        user=request.user,
        status='pending',
    )

   
    payment_method, _ = PaymentMethod.objects.get_or_create(
        user=request.user,
        payment_type='cash_on_delivery',
        provider='vodafone_cash',
        defaults={'description': 'Vodafone Cash via Paymob'}
    )

   
    payment = Payment.objects.create(
        user=request.user,
        amount=amount / 100,  
        status='pending',
        order=order,
        method=payment_method,
        paymob_order_id=paymob_order_id
    )

   
    payment_token = generate_payment_key(token, amount, paymob_order_id, phone)

    
    iframe_url = f"https://accept.paymobsolutions.com/api/acceptance/iframes/{settings.PAYMOB_IFRAME_ID_VF_CASH}?payment_token={payment_token}"
    return render(request, "payment.html", {"iframe_url": iframe_url})


@csrf_exempt
def paymob_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    paymob_order_id = str(data.get("order", {}).get("id"))
    success = data.get("success", False)

    if not paymob_order_id:
        return JsonResponse({"error": "Missing Paymob order ID"}, status=400)

    payment = Payment.objects.filter(paymob_order_id=paymob_order_id).first()

    if not payment:
        return JsonResponse({"error": "Payment not found"}, status=404)

    payment.status = "success" if success else "failed"
    payment.save()

    return JsonResponse({"message": "Payment status updated"})

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        data = json.loads(request.body)

        
        print("Callback Data Received:", data)

        success = data.get("success", False)
        order_id = data.get("order", {}).get("id")

        # Update payment in database
        if order_id:
            payment = Payment.objects.filter(order__id=order_id).first()
            if payment:
                payment.status = 'success' if success else 'failed'
                payment.save()

        return JsonResponse({"status": "received"})
    return JsonResponse({"error": "Method not allowed"}, status=405)