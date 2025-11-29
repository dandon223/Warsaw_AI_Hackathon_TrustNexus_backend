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
from .emails import parse_mails_to_dataframe
from django.views.decorators.csrf import ensure_csrf_cookie

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
        print(df.describe())
        return Response(
        {"message": "Done"}, 
        status=status.HTTP_201_CREATED
    )