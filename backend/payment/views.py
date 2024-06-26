import json
from django.shortcuts import render
import stripe
import os
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging

from .serializers import TransactionSerializer
from .models import Transaction
from rest_framework.generics import ListAPIView


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="payment.log",
)


class TransactionListView(ListAPIView):
    queryset = Transaction.objects.all().order_by("-created_at")
    serializer_class = TransactionSerializer


stripe.api_key = os.environ.get("STRIPE_API_KEY")
endpoint_secret = os.environ.get("ENDPOINT_SECRET")


@csrf_exempt
def create_payment_intent(request):
    payload = json.loads(request.body)
    amount = payload["amount"]

    try:
        paymentIntent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )
        logging.info("Payment Intent Created")
        Transaction.objects.create(
            payment_intent_id=paymentIntent.id,
            amount=amount,
            currency="usd".upper(),
            status="pending",  # Initially set the transaction as pending
        )
        return JsonResponse(paymentIntent, status=200)

    except stripe.error.StripeError as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=400)


@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        logging.error("Invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logging.error("Error verifying webhook signature: {}".format(str(e)))
        return HttpResponse(status=400)
    # Handle the event
    match event.type:
        case "payment_intent.succeeded":
            payment_intent = event.data.object
            handle_successful_payment(webhook_payment_intent=payment_intent)
            logging.info("Webhook triggered: Payment successful")
        case "payment_intent.created":
            logging.info("Webhook triggered: Payment intent created ")
        case "charge.succeeded":
            logging.info("Webhook triggered: Account charged ")
        case "charge.updated":
            logging.info("Webhook triggered: Account charge updated  ")
        case "payment_intent.requires_action":
            logging.info("Webhook triggered: Authentication in process")
        case "payment_intent.payment_failed":
            logging.info("Webhook triggered: Payment failed")
        case _:
            logging.error("Unhandled event type {}".format(event.type))

    return HttpResponse(status=200)


def handle_successful_payment(webhook_payment_intent):
    payment_intent_id = webhook_payment_intent["id"]
    amount_paid = webhook_payment_intent["amount_received"]
    currency = webhook_payment_intent["currency"]
    stripe_payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

    if stripe_payment_intent == webhook_payment_intent:
        try:
            # Create or update the transaction record
            transaction, created = Transaction.objects.update_or_create(
                payment_intent_id=payment_intent_id,
                defaults={
                    "amount": amount_paid,
                    "currency": currency.upper(),
                    "status": "succeeded",  # Mark the transaction as succeeded
                },
            )
            logging.info(
                f"Transaction {transaction.payment_intent_id} processed: {'created' if created else 'updated'}."
            )

        except Exception as e:
            logging.error(
                f"An error occurred while processing the transaction: {str(e)}"
            )

    else:
        logging.error(f"Response from webhook not verified")
