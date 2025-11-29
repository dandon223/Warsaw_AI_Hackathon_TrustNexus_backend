
from rest_framework import serializers
from .models import Email
class EmailSerializerGet(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Email
        fields = ["sender_name", "sender_email", "recipient_name", 
                  "recipient_email", "subject", "date", "message_content"]
        