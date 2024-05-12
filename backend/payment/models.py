from django.db import models


class Transaction(models.Model):
    payment_intent_id = models.CharField(max_length=255, unique=True)
    amount = models.BigIntegerField()
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
