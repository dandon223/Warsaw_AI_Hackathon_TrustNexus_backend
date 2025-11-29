from django.contrib import admin
from .models import Email
# Register your models here.
@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "sender", "receiver", "created_at")