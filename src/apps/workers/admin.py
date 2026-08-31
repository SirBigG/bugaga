from django.contrib import admin

from apps.accounts.admin import oidc_admin_site

from .models import WorkerState


@admin.register(WorkerState, site=oidc_admin_site)
class WorkerStateAdmin(admin.ModelAdmin):
    list_display = ("name", "integer_value", "updated_at")
    readonly_fields = ("name", "integer_value", "updated_at")

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
