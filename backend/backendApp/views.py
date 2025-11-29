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

class TestAPIView(APIView):  # type: ignore[misc]
    def get(self, request: Request):
        print(request)
        return Response(
        {"message": "Hi"}, 
        status=status.HTTP_201_CREATED
    )