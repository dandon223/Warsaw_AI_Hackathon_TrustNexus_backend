from django.urls import path

from .views import TestAPIView, EmailAPIView, SaveEmailsAPIView
urlpatterns = [
    path("test/", TestAPIView.as_view(), name="test"),
    path("emails/", EmailAPIView.as_view(), name="emails"),
    path("emails/save/", SaveEmailsAPIView.as_view(), name="save-emails"),
]