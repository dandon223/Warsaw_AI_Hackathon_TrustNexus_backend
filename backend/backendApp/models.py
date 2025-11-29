import uuid
from django.core.exceptions import ValidationError
from django.db import models

class Email(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=255)
    body = models.TextField()     # unlimited text
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject