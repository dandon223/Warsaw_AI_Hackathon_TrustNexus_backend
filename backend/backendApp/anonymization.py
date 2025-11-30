from cryptography.fernet import Fernet
from django.conf import settings

FERNET = Fernet(settings.EMAIL_ENCRYPTION_KEY.encode())


def encrypt_value(value: str) -> bytes:
	"""
	encrypts value using key
	"""
	return FERNET.encrypt(value.encode()).decode()


def decrypt_value(value: bytes) -> str:
	"""
	decrypts value using key
	"""
	return FERNET.decrypt(value.encode()).decode()
