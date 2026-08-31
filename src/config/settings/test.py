from .base import *  # noqa: F403

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
OIDC_CLIENT_ID = "test-client"
OIDC_CLIENT_SECRET = "test-secret"
OIDC_CALLBACK_URL = "https://api.example.com/oidc/callback/"
