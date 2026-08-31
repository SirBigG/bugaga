from django.apps import AppConfig


class WorkersConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "apps.workers"

    def ready(self):
        from . import admin  # noqa: F401
