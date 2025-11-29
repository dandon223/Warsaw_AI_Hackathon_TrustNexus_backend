from rest_framework import serializers

from .models import Email, LLMAnalysis


class EmailSerializerGet(serializers.ModelSerializer):
	class Meta:
		model = Email
		fields = [
			'sender_name',
			'sender_email',
			'recipient_name',
			'recipient_email',
			'subject',
			'date',
			'message_content',
			'summary',
		]


class LLMAnalysisSerializerGet(serializers.ModelSerializer):
	class Meta:
		model = LLMAnalysis
		fields = ['question', 'answer']
