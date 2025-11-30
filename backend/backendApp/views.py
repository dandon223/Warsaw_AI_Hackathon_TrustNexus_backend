import logging

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
from .test_connection import llm, query_llm

logger = logging.getLogger(__name__)

SUMMARY_PROMPT = """Extract key information and create a concise summary of the following email.
Focus on:
- Main topic or project
- Key requirements or specifications
- Important decisions or action items
- Risks or concerns mentioned
- Technical details (APIs, systems, integrations)

Email:
Subject: {subject}

Content: {content}

Provide a clear, concise summary (2-4 sentences) that captures the essential information."""


@ensure_csrf_cookie
def csrf(request: Request) -> JsonResponse:
	return JsonResponse({'detail': 'CSRF cookie set'})


class TestAPIView(APIView):  # type: ignore[misc]
	def get(self, request: Request):
		return Response({'message': 'Hi'}, status=status.HTTP_200_OK)


class EmailAPIView(APIView):  # type: ignore[misc]
	def post(self, request: Request):
		email_path = request.data.get('email_path')
		if email_path is None:
			return Response({'message': 'no email_path'}, status=status.HTTP_400_BAD_REQUEST)

		df = parse_mails_to_dataframe(email_path)
		total = len(df)
		processed = 0

		logger.info(f'Starting to process {total} emails incrementally')

		# Process each email individually and save immediately
		for idx, row in df.iterrows():
			try:
				# Generate summary for single email using LangChain llm
				subject = row.get('subject') or 'N/A'
				content = row.get('message_content') or 'N/A'
				prompt = SUMMARY_PROMPT.format(subject=subject, content=content)
				summary = llm.invoke(prompt).content

				# Save immediately to database
				Email.objects.create(
					sender_name=row.get('sender_name'),
					sender_email=row.get('sender_email'),
					recipient_name=row.get('recipient_name'),
					recipient_email=row.get('recipient_email'),
					subject=row.get('subject'),
					date=row.get('date'),
					message_content=row.get('message_content'),
					summary=summary,
					category=row.get('category'),
				)
				processed += 1
				logger.info(f'Processed email {processed}/{total}: {row.get("subject", "No subject")[:50]}')
			except Exception as e:
				logger.error(f'Error processing email {idx}: {e}')
				continue

		logger.info(f'Completed processing {processed}/{total} emails')
		return Response({'message': 'Done', 'total': total, 'processed': processed}, status=status.HTTP_201_CREATED)

	def get(self, request: Request) -> Response:
		emails = Email.objects.filter()
		serializer = EmailSerializerGet(emails, many=True)
		return Response(serializer.data)


class AnalyzeEmailsView(APIView):  # type: ignore[misc]
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


class SaveEmailsAPIView(APIView):  # type: ignore[misc]
	def post(self, request: Request) -> Response:
		email_path = request.data.get('email_path')
		if email_path is None:
			return Response({'message': 'no email_path'}, status=status.HTTP_400_BAD_REQUEST)
		emails_to_csv(email_path)
		return Response({'message': 'Done'}, status=status.HTTP_201_CREATED)


class SaveAnalyzeEmailsView(APIView):  # type: ignore[misc]
	def post(self, request: Request) -> Response:
		email_path = request.data.get('email_path')
		if email_path is None:
			return Response({'message': 'no email_path'}, status=status.HTTP_400_BAD_REQUEST)
		analysis_to_csv(email_path)
		return Response({'message': 'Done'}, status=status.HTTP_201_CREATED)
