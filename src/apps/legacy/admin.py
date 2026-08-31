from django.contrib import admin
from django.db import models
from django.forms import Textarea

from apps.accounts.admin import oidc_admin_site

from .models import (
    Advert,
    AdvertParserMap,
    Category,
    Link,
    News,
    ParsedItem,
    ParserMap,
    TelegramUser,
)


class StaffModelAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff


class ReadOnlyAdmin(StaffModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EditableWithoutDeleteAdmin(StaffModelAdmin):
    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Category, site=oidc_admin_site)
class CategoryAdmin(EditableWithoutDeleteAdmin):
    list_display = ("id", "title", "slug", "is_active", "level")
    list_filter = ("is_active", "level")
    search_fields = ("title", "slug")
    readonly_fields = ("lft", "rgt", "level", "tree_id", "parent")

    def has_add_permission(self, request):
        return False


class ParserMapAdminBase(EditableWithoutDeleteAdmin):
    list_display = ("id", "host", "link", "type", "is_active")
    list_filter = ("is_active", "type")
    search_fields = ("host", "link", "map")
    formfield_overrides = {models.TextField: {"widget": Textarea(attrs={"rows": 12, "cols": 100})}}


@admin.register(ParserMap, site=oidc_admin_site)
class ParserMapAdmin(ParserMapAdminBase):
    list_display = ParserMapAdminBase.list_display + ("category", "last_crawling")


@admin.register(AdvertParserMap, site=oidc_admin_site)
class AdvertParserMapAdmin(ParserMapAdminBase):
    list_display = ParserMapAdminBase.list_display + ("content_type",)


@admin.register(News, site=oidc_admin_site)
class NewsAdmin(EditableWithoutDeleteAdmin):
    list_display = ("id", "title", "created")
    search_fields = ("title", "description")
    formfield_overrides = {models.TextField: {"widget": Textarea(attrs={"rows": 30, "cols": 100})}}


@admin.register(Advert, site=oidc_admin_site)
class AdvertAdmin(StaffModelAdmin):
    list_display = ("id", "created", "category", "price", "link")
    list_editable = ("category",)
    list_filter = ("category", "created")
    search_fields = ("link", "data", "hash")
    readonly_fields = ("data", "link", "hash", "location", "price", "created")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ParsedItem, site=oidc_admin_site)
class ParsedItemAdmin(ReadOnlyAdmin):
    list_display = ("id", "created", "category", "hash")
    list_filter = ("category", "created")
    search_fields = ("hash", "data")


@admin.register(Link, site=oidc_admin_site)
class LinkAdmin(ReadOnlyAdmin):
    list_display = ("id", "is_parsed", "link")
    list_filter = ("is_parsed",)
    search_fields = ("link",)


@admin.register(TelegramUser, site=oidc_admin_site)
class TelegramUserAdmin(ReadOnlyAdmin):
    list_display = ("id", "telegram_key", "is_subscribed", "is_admin", "date_joined")
    list_filter = ("is_subscribed", "is_admin")
    search_fields = ("telegram_key",)
