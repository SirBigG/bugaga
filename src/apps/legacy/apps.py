from django.apps import AppConfig


class LegacyConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "apps.legacy"

    def ready(self):
        from . import admin  # noqa: F401
