from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentMethodViewSet
from .views import pay_with_vodafone_cash ,paymob_webhook
from . import views
router = DefaultRouter()
router.register('payments', PaymentViewSet, basename='payment')
router.register('methods', PaymentMethodViewSet, basename='paymentmethod')

urlpatterns = [
    path('', include(router.urls)),
    path('api/paymob/webhook/', paymob_webhook, name='paymob_webhook'),
   

]
