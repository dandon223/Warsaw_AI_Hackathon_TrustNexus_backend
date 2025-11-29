from django.urls import path

from .views import AnalyzeEmailsView, SaveEmailsAPIView, TestAPIView, EmailAPIView, SaveAnalyzeEmailsView
urlpatterns = [
    path("test/", TestAPIView.as_view(), name="test"), # for testing
    path("emails/", EmailAPIView.as_view(), name="emails"), # get and post
    path("emails/save/", SaveEmailsAPIView.as_view(), name="save-emails"), # post
    path("analyze/", AnalyzeEmailsView.as_view(), name="analyze-emails"), # get and post
    path("analyze/save", SaveAnalyzeEmailsView.as_view(), name="save-analyze-emails") # post
]