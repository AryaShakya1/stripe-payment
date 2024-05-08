from django.urls import path

from . import views

urlpatterns = [
    path("", views.create_payment_intent, name="index"),
]
