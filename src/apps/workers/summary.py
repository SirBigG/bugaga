import hashlib
import json
import logging
from datetime import UTC, datetime, time

import markdown
import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from transliterate import slugify

from apps.legacy.models import News, ParsedItem

logger = logging.getLogger(__name__)


def generate_summary(news_titles):
    prompt = (
        "Створи короткий і цікавий підсумок головних новин дня,"
        " акцентуючи увагу на ключових подіях та їх важливості."
        " Ocь список новин: \n" + "\n".join(news_titles)
    )
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.OPENAI_SUMMARY_MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=90,
    )
    if response.status_code != 200:
        logger.error("OpenAI summary failed with HTTP %s: %s", response.status_code, response.text[:1000])
        return None
    choices = response.json().get("choices") or []
    if not choices:
        return None
    return choices[0].get("message", {}).get("content") or None


def create_daily_summary(created_date=None):
    created_date = created_date or timezone.localdate()
    title = f"Підсумок новин за день {created_date}"
    if News.objects.filter(title=title).exists():
        logger.info("Daily summary already exists for %s", created_date)
        return False

    news_titles = []
    for raw_data in ParsedItem.objects.filter(created__date=created_date).values_list("data", flat=True):
        if not raw_data:
            continue
        try:
            data = json.loads(raw_data)
        except (TypeError, ValueError):
            logger.warning("Skipping invalid ParsedItem JSON while creating the daily summary")
            continue
        if data:
            news_titles.append(f"{data.get('title', '')}: {data.get('description', '')}")
    if not news_titles:
        return False

    summary = generate_summary(news_titles)
    if not summary:
        return False

    # Preserve the legacy 18:00 UTC timestamp used by AgroMega news URLs and ordering.
    created = datetime.combine(created_date, time(18), tzinfo=UTC)
    with transaction.atomic():
        if News.objects.select_for_update().filter(title=title).exists():
            return False
        news = News.objects.create(title=title, description=markdown.markdown(summary), created=created)
        payload = {
            "title": title,
            "description": summary[:100],
            "link": f"https://agromega.in.ua/news/{slugify(news.title)}-{news.id}.html",
        }
        payload_hash = hashlib.md5(
            ":".join(str(value) for value in payload.values()).encode(),
            usedforsecurity=False,
        ).hexdigest()
        ParsedItem.objects.create(data=json.dumps(payload), created=created, hash=payload_hash)
    return True
