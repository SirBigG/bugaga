import json
from datetime import timedelta
from urllib.parse import urlencode

from django.utils import timezone
from ninja import NinjaAPI
from ninja.errors import HttpError

from apps.legacy.models import Advert, News, ParsedItem

api = NinjaAPI(title="AgroMega Parser API", version="1.0.0", docs_url="/docs")
PAGE_SIZE = 20


def _json_object(value):
    try:
        parsed = json.loads(value)
    except TypeError, ValueError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _pagination_links(request, page, item_count, category=None):
    base_url = request.build_absolute_uri(request.path)

    def page_url(number):
        query = {"page": number}
        if category is not None:
            query = {"category": category, "page": number}
        return f"{base_url}?{urlencode(query)}"

    previous = page_url(page - 1) if page > 1 else None
    next_url = page_url(page + 1) if item_count else None
    return previous, next_url


@api.get("/health", tags=["system"], include_in_schema=False)
def health(request):
    return {"status": "ok"}


@api.get("/adverts", tags=["public"])
def adverts(request, page: int = 1, category: int | None = None):
    if page < 1:
        raise HttpError(400, "page must be greater than zero")
    query = Advert.objects.filter(created__gt=timezone.now() - timedelta(days=7))
    if category is not None:
        query = query.filter(category=category)
    rows = query.order_by("-created")[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]
    items = [{"data": _json_object(row.data), "link": row.link} for row in rows]
    previous, next_url = _pagination_links(request, page, len(items), category)
    return {"items": items, "next": next_url, "previous": previous}


@api.get("/news", tags=["public"])
def news_list(request, page: int = 1):
    if page < 1:
        raise HttpError(400, "page must be greater than zero")
    rows = ParsedItem.objects.order_by("-created")[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]
    items = [
        {
            "data": _json_object(row.data),
            "created": row.created.strftime("%d.%m.%Y") if row.created else "",
        }
        for row in rows
    ]
    previous, next_url = _pagination_links(request, page, len(items))
    return {"items": items, "next": next_url, "previous": previous}


@api.get("/news/sitemap", tags=["public"])
def news_sitemap(request):
    items = []
    for row in ParsedItem.objects.filter(data__contains="https://agromega.in.ua").order_by("-created"):
        data = _json_object(row.data)
        if data.get("link"):
            items.append({"loc": data["link"], "lastmod": row.created.isoformat() if row.created else ""})
    return {"items": items}


@api.get("/news/{uid}", tags=["public"])
def news_detail(request, uid: int):
    row = News.objects.filter(pk=uid).first()
    if row is None:
        raise HttpError(404, "News item not found")
    return {
        "title": row.title,
        "description": row.description,
        "image": row.image,
        "created": row.created.isoformat() if row.created else None,
    }


@api.get("/categories", tags=["public"])
def advert_categories(request):
    return list(
        Advert.objects.filter(
            created__gt=timezone.now() - timedelta(days=7),
            category__isnull=False,
        )
        .values_list("category", flat=True)
        .distinct()
    )
