import json
import logging

from celery import shared_task
from django.conf import settings
from django.db import transaction

from apps.legacy.models import ParsedItem, TelegramUser

from .bot import handle_update
from .ingestion import classify_adverts, parse_advert_links, parse_adverts, parse_news
from .locks import advisory_lock
from .models import WorkerState
from .summary import create_daily_summary
from .telegram import TelegramAPIError, TelegramClient

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True, name="bugaga.poll_telegram")
def poll_telegram():
    if not settings.BUGAGA_BOT_ENABLED:
        logger.debug("Skipping Telegram poll because BUGAGA_BOT_ENABLED is false")
        return {"status": "disabled"}
    if not settings.TELEGRAM_TOKEN:
        logger.error("Skipping Telegram poll because TELEGRAM_TOKEN is empty")
        return {"status": "misconfigured"}

    with advisory_lock("bugaga.telegram-poll") as acquired:
        if not acquired:
            return {"status": "locked"}

        state, _ = WorkerState.objects.get_or_create(name="telegram_update_offset")
        client = TelegramClient(settings.TELEGRAM_TOKEN)
        handled = 0
        try:
            updates = client.get_updates(
                offset=state.integer_value,
                timeout=settings.TELEGRAM_POLL_TIMEOUT,
            )
            for update in updates:
                handle_update(update, client)
                with transaction.atomic():
                    state.integer_value = int(update["update_id"]) + 1
                    state.save(update_fields=("integer_value", "updated_at"))
                handled += 1
        finally:
            client.close()
        return {"status": "ok", "updates": handled}


def _notification_text():
    lines = []
    for raw_data in ParsedItem.objects.order_by("-created").values_list("data", flat=True)[:3]:
        try:
            title = json.loads(raw_data).get("title", "")
        except (TypeError, ValueError):
            title = ""
        lines.append(f"<b>{title}</b> \n")
    return f"{''.join(lines)} \n<a href='https://agromega.in.ua/news/'>Докладніше</a>"


def notify_subscribers(client):
    text = _notification_text()
    sent = 0
    for user in TelegramUser.objects.filter(is_subscribed=True).iterator():
        with transaction.atomic():
            user = (
                TelegramUser.objects.select_for_update()
                .filter(pk=user.pk, is_subscribed=True)
                .first()
            )
            if user is None:
                continue
            try:
                client.send_text(user.telegram_key, text)
                sent += 1
            except TelegramAPIError as error:
                if error.error_code == 403:
                    user.is_subscribed = False
                    user.save(update_fields=("is_subscribed",))
                    logger.info(
                        "Deactivated Telegram subscriber %s after Telegram rejected delivery: %s",
                        user.pk,
                        error.description,
                    )
                else:
                    logger.exception("Could not send Telegram news to user %s", user.pk)
            except Exception:
                logger.exception("Could not send Telegram news to user %s", user.pk)
    return sent


@shared_task(ignore_result=True, name="bugaga.run_pipeline")
def run_pipeline():
    if not settings.BUGAGA_SCHEDULER_ENABLED:
        logger.warning("Skipping pipeline because BUGAGA_SCHEDULER_ENABLED is false")
        return {"status": "disabled"}

    with advisory_lock("bugaga.pipeline") as acquired:
        if not acquired:
            logger.warning("Skipping overlapping pipeline task")
            return {"status": "locked"}

        new_items = parse_news()
        sent = 0
        if new_items:
            client = TelegramClient(settings.TELEGRAM_TOKEN)
            try:
                sent = notify_subscribers(client)
            finally:
                client.close()
        links = parse_advert_links()
        adverts = parse_adverts()
        classified = classify_adverts()
        result = {
            "status": "ok",
            "news": new_items,
            "notifications": sent,
            "links": links,
            "adverts": adverts,
            "classified": classified,
        }
        logger.info("Pipeline completed: %s", result)
        return result


@shared_task(ignore_result=True, name="bugaga.create_daily_summary")
def daily_summary():
    if not settings.BUGAGA_SCHEDULER_ENABLED:
        logger.warning("Skipping daily summary because BUGAGA_SCHEDULER_ENABLED is false")
        return {"status": "disabled"}

    with advisory_lock("bugaga.daily-summary") as acquired:
        if not acquired:
            logger.warning("Skipping overlapping daily summary task")
            return {"status": "locked"}
        created = create_daily_summary()
        return {"status": "created" if created else "unchanged"}
