from django.urls import path
from .views import  OrderView, CreateOrderView

urlpatterns = [
    path('', OrderView.as_view(), name='order-list'),
    path('create/', CreateOrderView.as_view(), name='order-create'),
]