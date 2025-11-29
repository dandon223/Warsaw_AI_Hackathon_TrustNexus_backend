from django.contrib import admin
from .models import Email
# Register your models here.
@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_name', 'sender_email', 'recipient_name',
                        'recipient_email', 'subject', 'date', 'message_content', 'created_at')