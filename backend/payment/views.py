import json
from django.shortcuts import render
import stripe
import os
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


stripe.api_key = os.environ.get("STRIPE_API_KEY")
endpoint_secret = os.environ.get("ENDPOINT_SECRET")


def create_payment_intent(request):
    try:
        paymentIntent = stripe.PaymentIntent.create(
            amount=2000,
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )
        print("Payment Intent Created")
        return JsonResponse(paymentIntent, status=200)

    except stripe.error.StripeError as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=400)


@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    match event.type:
        case "payment_intent.succeeded":
            payment_intent = event.data.object
            print("Webhook triggered: Payment successful")
        case "payment_intent.created":
            print("Webhook triggered: Payment intent created ")
        case "charge.succeeded":
            print("Webhook triggered: Account charged ")
        case "charge.updated":
            print("Webhook triggered: Account charge updated  ")
        case "payment_intent.requires_action":
            print("Webhook triggered: Authentication in process")
        case "payment_intent.payment_failed":
            print("Webhook triggered: Payment failed")
        case _:
            print("Unhandled event type {}".format(event.type))

    return HttpResponse(status=200)
