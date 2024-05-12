from django.urls import path

from . import views

urlpatterns = [
    path("", views.create_payment_intent, name="index"),
    path("webhook/", views.my_webhook_view, name="webhook"),
    path("transactions/", views.TransactionListView.as_view(), name="transactions"),
]
