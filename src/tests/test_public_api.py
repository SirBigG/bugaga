import json
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from apps.legacy.models import Advert, Category, News, ParsedItem

LEGACY_TEST_MODELS = (Category, ParsedItem, Advert, News)


@pytest.fixture(scope="module", autouse=True)
def legacy_tables(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock(), connection.schema_editor() as schema_editor:
        for model in LEGACY_TEST_MODELS:
            schema_editor.create_model(model)
    yield
    with django_db_blocker.unblock(), connection.schema_editor() as schema_editor:
        for model in reversed(LEGACY_TEST_MODELS):
            schema_editor.delete_model(model)


@pytest.fixture
def category(db):
    return Category.objects.create(
        slug="grain",
        title="Зернові",
        is_active=True,
        lft=1,
        rgt=2,
        level=0,
        tree_id=1,
    )


@pytest.mark.django_db
def test_news_list_keeps_legacy_response_contract(client, category):
    ParsedItem.objects.create(
        data=json.dumps({"title": "Новина", "link": "https://agromega.in.ua/news/example"}),
        hash="news-hash",
        category=category,
        created=timezone.now(),
    )

    response = client.get("/news")

    assert response.status_code == 200
    assert response.json()["items"][0]["data"]["title"] == "Новина"
    assert response.json()["previous"] is None
    assert response.json()["next"] == "http://testserver/news?page=2"


@pytest.mark.django_db
def test_news_detail_keeps_legacy_fields(client):
    news = News.objects.create(
        title="Підсумок",
        description="Опис",
        image=None,
        created=timezone.now(),
    )

    response = client.get(f"/news/{news.pk}")

    assert response.status_code == 200
    assert response.json()["title"] == "Підсумок"
    assert response.json()["description"] == "Опис"
    assert response.json()["image"] is None


@pytest.mark.django_db
def test_adverts_and_categories_keep_legacy_contract(client):
    Advert.objects.create(
        data=json.dumps({"title": "Трактор"}),
        link="https://example.com/tractor",
        category=7,
        created=timezone.now() - timedelta(hours=1),
    )

    adverts_response = client.get("/adverts", {"category": 7})
    categories_response = client.get("/categories")

    assert adverts_response.status_code == 200
    assert adverts_response.json()["items"] == [{"data": {"title": "Трактор"}, "link": "https://example.com/tractor"}]
    assert adverts_response.json()["next"] == "http://testserver/adverts?category=7&page=2"
    assert categories_response.json() == [7]


@pytest.mark.django_db
def test_sitemap_includes_only_agromega_links(client, category):
    ParsedItem.objects.create(
        data=json.dumps({"link": "https://agromega.in.ua/news/one"}),
        hash="internal",
        category=category,
        created=timezone.now(),
    )
    ParsedItem.objects.create(
        data=json.dumps({"link": "https://example.com/news/two"}),
        hash="external",
        category=category,
        created=timezone.now(),
    )

    response = client.get("/news/sitemap")

    assert response.status_code == 200
    assert [item["loc"] for item in response.json()["items"]] == ["https://agromega.in.ua/news/one"]
