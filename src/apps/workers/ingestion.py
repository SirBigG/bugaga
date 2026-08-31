import hashlib
import json
import logging
from collections import Counter
from urllib.parse import urlparse

from django.db import connection, transaction
from django.utils import timezone

from apps.legacy.models import Advert, AdvertParserMap, Link, ParsedItem, ParserMap

from .images import load_image
from .parsers import parser_for

logger = logging.getLogger(__name__)


def _item_hash(parser_map, item):
    mapping = json.loads(parser_map.map)
    mapping.pop("encode", None)
    values = (str(item.get(key, "")) for key in mapping)
    return hashlib.md5((":".join(values) + parser_map.link).encode(), usedforsecurity=False).hexdigest()


def parse_news():
    created_count = 0
    for parser_map in ParserMap.objects.filter(is_active=True).iterator():
        try:
            pending = []
            for item in parser_for(parser_map).get_items():
                item_hash = _item_hash(parser_map, item)
                if ParsedItem.objects.filter(hash=item_hash).exists():
                    continue
                load_image(item, "news")
                pending.append(
                    ParsedItem(
                        hash=item_hash,
                        category_id=parser_map.category_id,
                        data=json.dumps(item),
                        created=timezone.now(),
                    )
                )
            if pending:
                ParsedItem.objects.bulk_create(pending)
                created_count += len(pending)
        except Exception:
            logger.exception("News parser failed for %s", parser_map.host)
    return created_count


def parse_advert_links():
    created_count = 0
    for parser_map in AdvertParserMap.objects.filter(is_active=True, content_type=1).iterator():
        try:
            consecutive_existing = 0
            for items in parser_for(parser_map):
                if consecutive_existing >= 10:
                    break
                pending = []
                for item in items:
                    raw_link = item.get("link")
                    if not raw_link:
                        continue
                    parsed = urlparse(raw_link)
                    clean_link = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    if Link.objects.filter(link=clean_link).exists():
                        consecutive_existing += 1
                    else:
                        pending.append(Link(link=clean_link, is_parsed=False))
                if pending:
                    Link.objects.bulk_create(pending)
                    created_count += len(pending)
        except Exception:
            logger.exception("Advert link parser failed for %s", parser_map.host)
    return created_count


def parse_adverts():
    created_count = 0
    for parser_map in AdvertParserMap.objects.filter(is_active=True, content_type=2).iterator():
        links = Link.objects.filter(is_parsed=False, link__contains=parser_map.host)
        for link in links.iterator():
            try:
                item = parser_for(parser_map, link=link.link).get_item()
                with transaction.atomic():
                    if item:
                        load_image(item, "adv")
                        Advert.objects.create(data=json.dumps(item), link=link.link, created=timezone.now())
                        created_count += 1
                    link.is_parsed = True
                    link.save(update_fields=("is_parsed",))
            except Exception:
                logger.exception("Advert parser failed for %s", link.link)
    return created_count


def _training_rows(limit_per_category=1000):
    if connection.vendor == "postgresql":
        sql = """
            SELECT category, data
            FROM (
                SELECT category, data,
                       row_number() OVER (PARTITION BY category) AS rownum
                FROM advert
                WHERE category IS NOT NULL
            ) AS categorized
            WHERE rownum <= %s
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, [limit_per_category])
            return cursor.fetchall()

    counts = Counter()
    rows = []
    for category, data in Advert.objects.exclude(category=None).values_list("category", "data").iterator():
        if counts[category] < limit_per_category:
            rows.append((category, data))
            counts[category] += 1
    return rows


def classify_adverts():
    from .text_classifier import classify

    try:
        training_rows = _training_rows()
        if not training_rows:
            logger.info("No categorized adverts available to train the classifier")
            return 0

        uncategorized = list(Advert.objects.filter(category=None).only("id", "data"))
        if not uncategorized:
            return 0

        predictions = classify(training_rows, [advert.data for advert in uncategorized])
        for advert, category in zip(uncategorized, predictions, strict=True):
            advert.category = category
        Advert.objects.bulk_update(uncategorized, ("category",))
        return len(uncategorized)
    except Exception:
        logger.exception("Advert classification failed")
        return 0
