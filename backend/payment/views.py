from django.shortcuts import render
import stripe
import os
from django.conf import settings
from django.http import JsonResponse

stripe.api_key = os.environ.get("STRIPE_API_KEY")  # here


def create_payment_intent(request):
    try:
        paymentIntent = stripe.PaymentIntent.create(
            amount=2000,
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )

        return JsonResponse(paymentIntent)
    except stripe.error.StripeError as e:
        return JsonResponse({"message": "Error", "error": str(e)})
