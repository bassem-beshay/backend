from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SiteSetting
from django.core.cache import cache
from rest_framework.decorators import api_view
import logging
# from transformers import pipeline
import requests

class CurrencyView(APIView):
    def get(self, request):
        currency = cache.get("site_currency")
        if currency:
            return Response({"currency": currency})
        
        site_setting = SiteSetting.objects.first()
        if site_setting and site_setting.currency:
            currency = site_setting.currency
            cache.set("site_currency", currency, timeout=60 * 60 * 24 * 7)  # Cache for 7 days
            return Response({"currency": currency})
        else:
            return Response({"error": "Site settings not configured."}, status=status.HTTP_404_NOT_FOUND)

# Load the chatbot model

# chatbot = pipeline("text-generation", model="distilgpt2")

# @api_view(["POST"])
# def chatbot_response(request):
#     user_msg = request.data.get("message", "")
#     history = request.data.get("history", [])

#     site_info = (
#         "Welcome to SourceCode — an eCommerce multivendor website.\n"
#         "Vendors can register, create stores, and add products.\n"
#         "Buyers can browse, search, and order with multiple payment options.\n"
#         "Popular categories: Fashion, Electronics, Kitchen tools.\n"
#     )

#     conversation_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
#     prompt = f"{site_info}\n{conversation_history}\nUser: {user_msg}\nBot:"

#     response_text = chatbot(prompt, max_length=300, do_sample=True)[0]["generated_text"]
#     reply = response_text.split("Bot:")[-1].split("User:")[0].strip()
#     return Response({"reply": reply})



logger = logging.getLogger(__name__) 

OPENROUTER_API_KEY = "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"

MODEL = "mistralai/mistral-7b-instruct"
SYSTEM_PROMPT = """
You are ShopAssist, the AI assistant for VendorHub Website.

1. Product inquiries and recommendations
2. Order tracking and status updates
3. Vendor-specific questions
4. Return/refund policies
5. Payment and shipping options
"""
@api_view(["POST"])
def chatbot_response(request):
    """
    Handle chatbot requests with optimized error handling and e-commerce context.
    """
    user_msg = request.data.get("message", "").strip()
    history = request.data.get("history", [])

    if not user_msg:
        return Response(
            {"reply": "Please provide a message to continue."},
            status=status.HTTP_400_BAD_REQUEST
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(
        {"role": "assistant" if item["role"] == "bot" else "user", "content": item["content"]}
        for item in history
    )
    messages.append({"role": "user", "content": user_msg})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0.9,
                "max_tokens": 500,
            },
            timeout=10
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"].strip()
        return Response({"reply": _format_ecommerce_response(reply)})

    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API error: {str(e)}")
        return Response(
            {"reply": "Unable to connect to the chatbot service. Please try again later."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return Response(
            {"reply": "An unexpected error occurred. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _format_ecommerce_response(text: str) -> str:
    """
    Post-process the AI response for e-commerce context.
    """
    text = text.replace("```", "")  
    if len(text) > 1000:
        text = text[:1000] + "... [response truncated]"
    return text.strip()