import logging

from django.db import transaction
from django.utils import timezone

from apps.legacy.models import TelegramUser

logger = logging.getLogger(__name__)

START_RESPONSE = (
    "Дякуємо! Ви успішно підписались на агроновини! "
    "Як тільки з'являться публікації вони відразу приходитимуть Вам. "
    "Для того щоб запропонувати додати Ваш улюблений ресурс до списку відслідковування, "
    "зв'яжіться з нами через форму "
    "<a href='https://agromega.in.ua/feedback/'>зворотнього зв'язку</a>."
)


@transaction.atomic
def subscribe(chat_id):
    telegram_key = str(chat_id)
    user = TelegramUser.objects.select_for_update().filter(telegram_key=telegram_key).first()
    if user is None:
        user = TelegramUser(telegram_key=telegram_key, date_joined=timezone.now(), is_admin=False)
    user.is_subscribed = True
    user.save()
    return user


def handle_update(update, client):
    message = update.get("message") or {}
    text = str(message.get("text") or "").strip()
    command = text.split(maxsplit=1)[0].split("@", maxsplit=1)[0]
    if command != "/start":
        return False

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if chat_id is None:
        logger.warning("Ignoring /start update without a chat id: %s", update.get("update_id"))
        return False

    subscribe(chat_id)
    client.send_text(chat_id, START_RESPONSE)
    return True
