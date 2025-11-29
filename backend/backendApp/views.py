import uuid
from typing import Any, Dict, List

from django.db import transaction
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import pandas as pd

from .test_connection import query_llm
from .emails import parse_mails_to_dataframe
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Email

@ensure_csrf_cookie
def csrf(request: Request) -> JsonResponse:
    return JsonResponse({"detail": "CSRF cookie set"})
class TestAPIView(APIView):  # type: ignore[misc]
    def get(self, request: Request):
        return Response(
        {"message": "Hi"}, 
        status=status.HTTP_200_OK
    )


class EmailAPIView(APIView):  # type: ignore[misc]

    def post(self, request: Request) -> Response:
        email_path = request.data.get("email_path")
        if email_path is None:
            return Response(
            {"message": "no email_path"}, 
            status=status.HTTP_400_BAD_REQUEST 
            )

        df = parse_mails_to_dataframe(email_path)
        print(df)
        for _, row in df.iterrows():
            Email.objects.get_or_create(
                sender_name=row['sender_name'],
                sender_email=row['sender_email'],
                recipient_name=row['recipient_name'],
                recipient_email=row['recipient_email'],
                subject=row['subject'],
                date=row['date'],
                message_content=row['message_content'],
            )
        return Response(
        {"message": "Done"}, 
        status=status.HTTP_201_CREATED
    )

class AnalyzeEmailsView(APIView):  # type: ignore[misc]
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        emails = Email.objects.all()
        if not emails.exists():
            raise NotFound("No emails found")
        
        text_request = request.data.get("text", "")

        resp = query_llm(text_request, list(emails))
        print(text_request)
        
        return Response({"emails": {resp}}, status=status.HTTP_200_OK)