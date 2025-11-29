from django.conf import settings
from cryptography.fernet import Fernet

FERNET = Fernet(settings.EMAIL_ENCRYPTION_KEY.encode())

def encrypt_value(value):
    return FERNET.encrypt(value.encode()).decode()

def decrypt_value(value):
    return FERNET.decrypt(value.encode()).decode()