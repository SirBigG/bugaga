import json
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from apps.accounts.admin import oidc_admin_site
from apps.legacy.models import Category, News, ParsedItem, TelegramUser
from apps.workers.bot import START_RESPONSE, handle_update
from apps.workers.models import WorkerState
from apps.workers.summary import create_daily_summary
from apps.workers.tasks import notify_subscribers, poll_telegram, run_pipeline
from apps.workers.telegram import TelegramAPIError, TelegramClient

LEGACY_WORKER_TEST_MODELS = (Category, TelegramUser, ParsedItem, News)


@pytest.fixture(scope="module", autouse=True)
def worker_legacy_tables(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock(), connection.schema_editor() as schema_editor:
        for model in LEGACY_WORKER_TEST_MODELS:
            schema_editor.create_model(model)
    yield
    with django_db_blocker.unblock(), connection.schema_editor() as schema_editor:
        for model in reversed(LEGACY_WORKER_TEST_MODELS):
            schema_editor.delete_model(model)


class FakeTelegramClient:
    updates = []

    def __init__(self, token):
        self.token = token
        self.sent = []
        self.requested_offset = None

    def get_updates(self, *, offset=None, timeout=2):
        self.requested_offset = offset
        return self.updates

    def send_text(self, chat_id, text, *, parse_mode="HTML"):
        self.sent.append((str(chat_id), text, parse_mode))

    def close(self):
        pass


@pytest.mark.django_db
def test_start_command_subscribes_user_and_preserves_legacy_response():
    client = FakeTelegramClient("token")

    handled = handle_update(
        {"update_id": 1, "message": {"text": "/start", "chat": {"id": 12345}}},
        client,
    )

    assert handled is True
    assert TelegramUser.objects.get(telegram_key="12345").is_subscribed is True
    assert client.sent == [("12345", START_RESPONSE, "HTML")]


@pytest.mark.django_db
def test_forbidden_subscriber_is_deactivated_and_start_reactivates_them():
    user = TelegramUser.objects.create(
        telegram_key="12345",
        date_joined=timezone.now(),
        is_subscribed=True,
        is_admin=False,
    )
    ParsedItem.objects.create(
        data=json.dumps({"title": "Новина"}),
        hash="blocked-subscriber-news",
        created=timezone.now(),
    )
    client = FakeTelegramClient("token")
    client.send_text = lambda *args, **kwargs: (_ for _ in ()).throw(
        TelegramAPIError("sendMessage", 403, "Forbidden: bot was blocked by the user")
    )

    assert notify_subscribers(client) == 0
    user.refresh_from_db()
    assert user.is_subscribed is False

    skipped_client = FakeTelegramClient("token")
    assert notify_subscribers(skipped_client) == 0
    assert skipped_client.sent == []

    start_client = FakeTelegramClient("token")
    assert handle_update(
        {"update_id": 2, "message": {"text": "/start", "chat": {"id": 12345}}},
        start_client,
    ) is True
    user.refresh_from_db()
    assert user.is_subscribed is True


@pytest.mark.django_db
def test_non_forbidden_telegram_error_does_not_deactivate_subscriber():
    user = TelegramUser.objects.create(
        telegram_key="67890",
        date_joined=timezone.now(),
        is_subscribed=True,
        is_admin=False,
    )
    client = FakeTelegramClient("token")
    client.send_text = lambda *args, **kwargs: (_ for _ in ()).throw(
        TelegramAPIError("sendMessage", 429, "Too Many Requests")
    )

    assert notify_subscribers(client) == 0
    user.refresh_from_db()
    assert user.is_subscribed is True


def test_telegram_client_exposes_api_error_code():
    response = SimpleNamespace(
        status_code=403,
        json=lambda: {
            "ok": False,
            "error_code": 403,
            "description": "Forbidden: bot was blocked by the user",
        },
    )
    session = SimpleNamespace(post=lambda *args, **kwargs: response)
    client = TelegramClient("token", session=session)

    with pytest.raises(TelegramAPIError) as raised:
        client.send_text("12345", "Новина")

    assert raised.value.error_code == 403
    assert raised.value.description == "Forbidden: bot was blocked by the user"


@pytest.mark.django_db
@override_settings(BUGAGA_BOT_ENABLED=True, TELEGRAM_TOKEN="token", TELEGRAM_POLL_TIMEOUT=1)
def test_celery_poll_persists_update_offset():
    FakeTelegramClient.updates = [
        {"update_id": 40, "message": {"text": "/start", "chat": {"id": 9001}}},
        {"update_id": 41, "message": {"text": "ignored", "chat": {"id": 9001}}},
    ]
    with patch("apps.workers.tasks.TelegramClient", FakeTelegramClient):
        result = poll_telegram()

    assert result == {"status": "ok", "updates": 2}
    assert WorkerState.objects.get(name="telegram_update_offset").integer_value == 42
    assert TelegramUser.objects.get(telegram_key="9001").is_subscribed is True


@pytest.mark.django_db
def test_worker_schedules_are_installed_disabled_by_default():
    call_command("install_worker_schedules")

    schedules = PeriodicTask.objects.filter(name__startswith="AgroMega ")
    assert set(schedules.values_list("task", flat=True)) == {
        "bugaga.poll_telegram",
        "bugaga.run_pipeline",
        "bugaga.create_daily_summary",
    }
    assert schedules.filter(enabled=True).exists() is False

    telegram = schedules.get(task="bugaga.poll_telegram")
    telegram.enabled = True
    telegram.save(update_fields=("enabled",))
    call_command("install_worker_schedules")
    assert PeriodicTask.objects.get(pk=telegram.pk).enabled is True


def test_oidc_staff_can_manage_periodic_tasks(rf):
    request = rf.get("/admin/django_celery_beat/periodictask/")
    request.user = SimpleNamespace(is_active=True, is_staff=True)

    model_admin = oidc_admin_site._registry[PeriodicTask]

    assert model_admin.has_view_permission(request) is True
    assert model_admin.has_change_permission(request) is True


@pytest.mark.django_db
def test_periodic_tasks_are_visible_in_oidc_admin(client):
    staff = User.objects.create_user(username="scheduler-admin", is_staff=True)
    client.force_login(staff)

    response = client.get(reverse("admin:django_celery_beat_periodictask_changelist"))

    assert response.status_code == 200


@pytest.mark.django_db
@override_settings(BUGAGA_SCHEDULER_ENABLED=False)
def test_pipeline_feature_gate_prevents_legacy_writes():
    with patch("apps.workers.tasks.parse_news") as parse_news:
        result = run_pipeline()

    assert result == {"status": "disabled"}
    parse_news.assert_not_called()


@pytest.mark.django_db
def test_daily_summary_is_idempotent():
    created_date = date(2026, 8, 31)
    ParsedItem.objects.create(
        data=json.dumps({"title": "Врожай", "description": "Опис"}),
        hash="daily-source",
        created=timezone.make_aware(timezone.datetime(2026, 8, 31, 12)),
    )

    with patch("apps.workers.summary.generate_summary", return_value="Короткий підсумок") as generate:
        assert create_daily_summary(created_date) is True
        assert create_daily_summary(created_date) is False

    assert generate.call_count == 1
    assert News.objects.filter(title=f"Підсумок новин за день {created_date}").count() == 1
