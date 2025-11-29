from django.urls import path

from .views import AnalyzeEmailsView, SaveEmailsAPIView, TestAPIView, EmailAPIView
urlpatterns = [
    path("test/", TestAPIView.as_view(), name="test"),
    path("emails/", EmailAPIView.as_view(), name="emails"),
    path("emails/save/", SaveEmailsAPIView.as_view(), name="save-emails"),
    path("analyze/", AnalyzeEmailsView.as_view(), name="analyze_emails"),
]