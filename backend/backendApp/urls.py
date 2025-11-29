from django.urls import path

from .views import AnalyzeEmailsView, TestAPIView, EmailAPIView
urlpatterns = [
    path("test/", TestAPIView.as_view(), name="test"),
    path("emails/", EmailAPIView.as_view(), name="emails"),
    path("analyze/", AnalyzeEmailsView.as_view(), name="analyze_emails"),
]