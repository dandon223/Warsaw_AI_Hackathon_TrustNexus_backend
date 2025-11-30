import uuid
from django.core.exceptions import ValidationError
from django.db import models
from .anonymization import encrypt_value, decrypt_value

class Email(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encrypted_sender_name = models.TextField(null=True)
    encrypted_sender_email = models.TextField(null=True)
    encrypted_recipient_name = models.TextField(null=True)
    encrypted_recipient_email = models.TextField(null=True)
    encrypted_subject = models.TextField(null=True)
    encrypted_summary = models.TextField(null=True)
    encrypted_date = models.TextField(null=True)
    encrypted_message_content = models.TextField(null=True)
    encrypted_category = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('encrypted_sender_name', 'encrypted_sender_email', 'encrypted_recipient_name',
                           'encrypted_recipient_email', 'encrypted_subject', 'encrypted_date', 'encrypted_message_content',)

    # -------- PROPERTIES FOR DECRYPTED ACCESS --------
    @property
    def sender_name(self):
        return decrypt_value(self.encrypted_sender_name) if self.encrypted_sender_name else None

    @sender_name.setter
    def sender_name(self, value):
        self.encrypted_sender_name = encrypt_value(value) if value else None

    @property
    def summary(self):
        return decrypt_value(self.encrypted_summary) if self.encrypted_summary else None

    @summary.setter
    def summary(self, value):
        self.encrypted_summary = encrypt_value(value) if value else None

    @property
    def category(self):
        return decrypt_value(self.encrypted_category) if self.encrypted_category else None

    @category.setter
    def category(self, value):
        self.encrypted_category = encrypt_value(value) if value else None

    @property
    def sender_email(self):
        return decrypt_value(self.encrypted_sender_email) if self.encrypted_sender_email else None

    @sender_email.setter
    def sender_email(self, value):
        self.encrypted_sender_email = encrypt_value(value) if value else None

    @property
    def recipient_name(self):
        return decrypt_value(self.encrypted_recipient_name) if self.encrypted_recipient_name else None

    @recipient_name.setter
    def recipient_name(self, value):
        self.encrypted_recipient_name = encrypt_value(value) if value else None

    @property
    def recipient_email(self):
        return decrypt_value(self.encrypted_recipient_email) if self.encrypted_recipient_email else None

    @recipient_email.setter
    def recipient_email(self, value):
        self.encrypted_recipient_email = encrypt_value(value) if value else None

    @property
    def subject(self):
        return decrypt_value(self.encrypted_subject) if self.encrypted_subject else None

    @subject.setter
    def subject(self, value):
        self.encrypted_subject = encrypt_value(value) if value else None

    @property
    def date(self):
        return decrypt_value(self.encrypted_date) if self.encrypted_date else None

    @date.setter
    def date(self, value):
        self.encrypted_date = encrypt_value(value) if value else None

    @property
    def message_content(self):
        return decrypt_value(self.encrypted_message_content) if self.encrypted_message_content else None

    @message_content.setter
    def message_content(self, value):
        self.encrypted_message_content = encrypt_value(value) if value else None

    def __str__(self):
        return self.subject


class LLMAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encrypted_question = models.TextField(null=True) 
    encrypted_answer = models.TextField(null=True)

    # -------- PROPERTIES FOR DECRYPTED ACCESS --------
    @property
    def question(self):
        return decrypt_value(self.encrypted_question) if self.encrypted_question else None

    @question.setter
    def question(self, value):
        self.encrypted_question = encrypt_value(value) if value else None

    @property
    def answer(self):
        return decrypt_value(self.encrypted_answer) if self.encrypted_answer else None

    @answer.setter
    def answer(self, value):
        self.encrypted_answer = encrypt_value(value) if value else None

    def __str__(self):
        return self.encrypted_question