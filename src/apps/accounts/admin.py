from urllib.parse import urlencode

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect
from django.urls import reverse

from .models import OIDCIdentity


class OIDCAdminSite(AdminSite):
    site_header = "AgroMega API"
    site_title = "AgroMega API Admin"
    index_title = "Керування парсерами та новинами"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def login(self, request, extra_context=None):
        if self.has_permission(request):
            return redirect(self.index_url)
        query = urlencode({"next": request.GET.get("next") or "/admin/"})
        return redirect(f"{reverse('oidc-login')}?{query}")

    def logout(self, request, extra_context=None):
        return redirect("oidc-logout")

    @property
    def index_url(self):
        return reverse("admin:index")


oidc_admin_site = OIDCAdminSite(name="admin")
oidc_admin_site.register(User, UserAdmin)
oidc_admin_site.register(Group, GroupAdmin)


@admin.register(OIDCIdentity, site=oidc_admin_site)
class OIDCIdentityAdmin(admin.ModelAdmin):
    list_display = ("issuer", "subject", "user", "last_synced_at")
    search_fields = ("issuer", "subject", "user__email")
    readonly_fields = ("issuer", "subject", "user", "last_synced_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
