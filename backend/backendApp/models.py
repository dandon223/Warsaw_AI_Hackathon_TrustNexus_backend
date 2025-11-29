import uuid
from django.core.exceptions import ValidationError
from django.db import models

class Email(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_name = models.TextField() 
    sender_email = models.TextField()
    recipient_name = models.TextField() 
    recipient_email = models.TextField()
    subject = models.TextField()
    date = models.TextField()
    message_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('sender_name', 'sender_email', 'recipient_name',
                           'recipient_email', 'subject', 'date', 'message_content')
    
    def __str__(self):
        return self.subject