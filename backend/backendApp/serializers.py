
from rest_framework import serializers
from .models import Email, LLMAnalysis
class EmailSerializerGet(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Email
        fields = ["sender_name", "sender_email", "recipient_name", 
                  "recipient_email", "subject", "date", "message_content", "summary", "project_name", "timeline", "category"]

class EmailSerializerPost(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Email
        fields = ["sender_name", "sender_email", "recipient_name", 
                  "recipient_email", "subject", "date", "summary", "project_name", "timeline", "category"]

class LLMAnalysisSerializerGet(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = LLMAnalysis
        fields = ["question", "answer"]