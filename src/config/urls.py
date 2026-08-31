from django.urls import path

from apps.accounts import views as oidc_views
from apps.accounts.admin import oidc_admin_site
from apps.api.api import api

urlpatterns = [
    path("oidc/login/", oidc_views.oidc_login, name="oidc-login"),
    path("oidc/callback/", oidc_views.oidc_callback, name="oidc-callback"),
    path("oidc/logout/", oidc_views.oidc_logout, name="oidc-logout"),
    path("admin/", oidc_admin_site.urls),
    path("", api.urls),
]
