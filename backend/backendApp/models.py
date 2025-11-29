import uuid
from django.core.exceptions import ValidationError
from django.db import models

class Email(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_name = models.TextField(null=True) 
    sender_email = models.TextField(null=True)
    recipient_name = models.TextField(null=True) 
    recipient_email = models.TextField(null=True)
    subject = models.TextField(null=True)
    date = models.TextField(null=True)
    message_content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('sender_name', 'sender_email', 'recipient_name',
                           'recipient_email', 'subject', 'date', 'message_content')
    
    def __str__(self):
        return self.subject

class LLMAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField(null=True) 
    answer = models.TextField(null=True)

    def __str__(self):
        return self.question