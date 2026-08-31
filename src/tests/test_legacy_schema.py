from django.db import models

from apps.legacy.models import (
    Advert,
    AdvertParserMap,
    Category,
    Link,
    News,
    ParsedItem,
    ParserMap,
    TelegramUser,
    UserCategoryAssociation,
)


def test_legacy_models_match_production_table_names():
    expected_tables = {
        Advert: "advert",
        AdvertParserMap: "advertparsemap",
        Category: "category",
        Link: "link",
        News: "news",
        ParsedItem: "parseditem",
        ParserMap: "parsermap",
        TelegramUser: "tusers",
        UserCategoryAssociation: "user_category_association",
    }

    for model, table_name in expected_tables.items():
        assert model._meta.db_table == table_name
        assert model._meta.managed is False


def test_user_category_association_matches_composite_primary_key():
    assert isinstance(UserCategoryAssociation._meta.pk, models.CompositePrimaryKey)
    assert UserCategoryAssociation._meta.pk.field_names == ("telegram_user", "category")
    assert UserCategoryAssociation._meta.get_field("telegram_user").column == "user_id"
    assert UserCategoryAssociation._meta.get_field("category").column == "category_id"
    assert TelegramUser._meta.get_field("categories").remote_field.through is UserCategoryAssociation


def test_production_only_legacy_tables_are_not_assumed():
    from apps.legacy import models as legacy_models

    assert not hasattr(legacy_models, "Price")
    assert not hasattr(legacy_models, "PriceParserMap")
