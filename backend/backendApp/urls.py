from django.urls import path

from .views import TestAPIView, EmailAPIView
urlpatterns = [
    path("test/", TestAPIView.as_view(), name="test"),
    path("emails/", EmailAPIView.as_view(), name="emails"),
]