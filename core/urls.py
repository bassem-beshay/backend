from django.urls import path
from .views import CurrencyView,chatbot_response

urlpatterns = [
    path('currency/', CurrencyView.as_view(), name='currency-api'),
    path("chatbot/", chatbot_response, name="chatbot-response"),
]