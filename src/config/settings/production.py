from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

if SECRET_KEY == "unsafe-development-only":  # noqa: F405
    raise ImproperlyConfigured("DJANGO_SECRET_KEY is required in production.")
if not OIDC_CLIENT_ID or not OIDC_CLIENT_SECRET or not OIDC_CALLBACK_URL:  # noqa: F405
    raise ImproperlyConfigured("OIDC_CLIENT_ID, OIDC_CLIENT_SECRET and OIDC_CALLBACK_URL are required.")

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
