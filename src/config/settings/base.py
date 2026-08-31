import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-only")
DEBUG = False

ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "apps.accounts",
    "apps.legacy",
    "apps.workers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "NAME": os.getenv("POSTGRES_DB", "bugagadb"),
        "USER": os.getenv("POSTGRES_USER", "bugaga"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "uk"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOGIN_URL = "/oidc/login/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/"

OIDC_ISSUER = os.getenv("OIDC_ISSUER", "https://agromega.in.ua/o").rstrip("/")
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID", "")
OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET", "")
OIDC_SCOPES = os.getenv("OIDC_SCOPES", "openid profile email")
OIDC_CALLBACK_URL = os.getenv("OIDC_CALLBACK_URL", "")
OIDC_POST_LOGOUT_REDIRECT_URL = os.getenv("OIDC_POST_LOGOUT_REDIRECT_URL", "")
OIDC_SYNC_SUPERUSER = os.getenv("OIDC_SYNC_SUPERUSER", "false").lower() in {"1", "true", "yes"}

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_POLL_TIMEOUT = int(os.getenv("TELEGRAM_POLL_TIMEOUT", "2"))
TELEGRAM_POLL_INTERVAL_SECONDS = int(os.getenv("TELEGRAM_POLL_INTERVAL_SECONDS", "5"))
SCHEDULER_INTERVAL = int(os.getenv("SCHEDULER_INTERVAL", "30"))
BUGAGA_BOT_ENABLED = os.getenv("BUGAGA_BOT_ENABLED", "false").lower() in {"1", "true", "yes"}
BUGAGA_SCHEDULER_ENABLED = os.getenv("BUGAGA_SCHEDULER_ENABLED", "false").lower() in {"1", "true", "yes"}
BUGAGA_SUMMARY_TIME_ZONE = os.getenv("BUGAGA_SUMMARY_TIME_ZONE", "Europe/Kyiv")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_SUMMARY_MODEL = os.getenv("OPENAI_SUMMARY_MODEL", "gpt-4o")
DO_SPACE_KEY = os.getenv("DO_SPACE_KEY", "")
DO_SPACE_SECRET = os.getenv("DO_SPACE_SECRET", "")
DO_SPACE_REGION = os.getenv("DO_SPACE_REGION", "")
DO_SPACE_NAME = os.getenv("DO_SPACE_NAME", "")

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True
CELERY_TASK_IGNORE_RESULT = True
CELERY_TASK_TRACK_STARTED = False
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 8
SESSION_COOKIE_NAME = "agromega_api_sessionid"
CSRF_COOKIE_NAME = "agromega_api_csrftoken"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
