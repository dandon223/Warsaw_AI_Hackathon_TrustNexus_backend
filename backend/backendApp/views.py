from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .emails import analysis_to_csv, emails_to_csv, parse_mails_to_dataframe
from .llm_summary import add_summary_to_dataframe
from .models import Email, LLMAnalysis
from .serializers import EmailSerializerGet, LLMAnalysisSerializerGet
from .test_connection import query_llm


@ensure_csrf_cookie
def csrf(request: Request) -> JsonResponse:
	return JsonResponse({'detail': 'CSRF cookie set'})


class TestAPIView(APIView):
	def get(self, request: Request):
		return Response({'message': 'Hi'}, status=status.HTTP_200_OK)


class EmailAPIView(APIView):
	def post(self, request: Request):
		email_path = request.data.get('email_path')
		if email_path is None:
			return Response({'message': 'no email_path'}, status=status.HTTP_400_BAD_REQUEST)

		df = parse_mails_to_dataframe(email_path)
		summaried_df = add_summary_to_dataframe(df)
		emails_to_create = []
		for _, row in summaried_df.iterrows():
			emails_to_create.append(
				Email(
					sender_name=row['sender_name'],
					sender_email=row['sender_email'],
					recipient_name=row['recipient_name'],
					recipient_email=row['recipient_email'],
					subject=row['subject'],
					date=row['date'],
					message_content=row['message_content'],
					summary=row['summary'],
				)
			)

		Email.objects.bulk_create(emails_to_create, ignore_conflicts=True)
		return Response({'message': 'Done'}, status=status.HTTP_201_CREATED)

	def get(self, request: Request) -> Response:
		emails = Email.objects.filter()
		serializer = EmailSerializerGet(emails, many=True)
		return Response(serializer.data)


class AnalyzeEmailsView(APIView):
	permission_classes = [AllowAny]

	def post(self, request) -> Response:
		emails = Email.objects.all()
		if not emails.exists():
			raise NotFound('No emails found')

		text_request = request.data.get('text', '')

		data = [model_to_dict(email) for email in emails]

		resp = query_llm(text_request, data)
		LLMAnalysis.objects.create(question=text_request, answer=resp)
		return Response({'emails': {resp}}, status=status.HTTP_200_OK)

	def get(self, request: Request) -> Response:
		emails = LLMAnalysis.objects.filter()
		serializer = LLMAnalysisSerializerGet(emails, many=True)
		return Response(serializer.data)


class SaveEmailsAPIView(APIView):
	def post(self, request: Request) -> Response:
		email_path = request.data.get('email_path')
		if email_path is None:
			return Response({'message': 'no email_path'}, status=status.HTTP_400_BAD_REQUEST)
		emails_to_csv(email_path)
		return Response({'message': 'Done'}, status=status.HTTP_201_CREATED)


class SaveAnalyzeEmailsView(APIView):
	def post(self, request: Request) -> Response:
		email_path = request.data.get('email_path')
		if email_path is None:
			return Response({'message': 'no email_path'}, status=status.HTTP_400_BAD_REQUEST)
		analysis_to_csv(email_path)
		return Response({'message': 'Done'}, status=status.HTTP_201_CREATED)
