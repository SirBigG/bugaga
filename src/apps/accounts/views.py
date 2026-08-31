import logging

from authlib.integrations.base_client import OAuthError
from django.conf import settings
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET

from .oidc import oauth
from .services import synchronize_oidc_user

logger = logging.getLogger(__name__)


def _safe_next(request, candidate):
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=not settings.DEBUG,
    ):
        return candidate
    return "/admin/"


@require_GET
def oidc_login(request):
    request.session["oidc_next"] = _safe_next(request, request.GET.get("next"))
    redirect_uri = settings.OIDC_CALLBACK_URL or request.build_absolute_uri(reverse("oidc-callback"))
    return oauth.agromega.authorize_redirect(request, redirect_uri)


@require_GET
def oidc_callback(request):
    try:
        token = oauth.agromega.authorize_access_token(request)
        # Authlib's token["userinfo"] is normally derived from the ID token.
        # Some providers expose custom authorization claims only from the
        # UserInfo endpoint, so always fetch it and let it override ID-token
        # claims.
        userinfo = dict(token.get("userinfo") or {})
        userinfo.update(dict(oauth.agromega.userinfo(token=token)))
    except OAuthError:
        logger.warning("OIDC callback validation failed", exc_info=True)
        return HttpResponseForbidden("OIDC authentication failed.")
    try:
        user = synchronize_oidc_user(userinfo)
    except PermissionDenied as exc:
        logger.warning(
            "OIDC user rejected: is_staff=%r is_superuser=%r claim_keys=%s",
            userinfo.get("is_staff"),
            userinfo.get("is_superuser"),
            sorted(userinfo),
        )
        return HttpResponseForbidden(str(exc))

    django_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    if token.get("id_token"):
        request.session["oidc_id_token"] = token["id_token"]
    return redirect(_safe_next(request, request.session.pop("oidc_next", None)))


@require_GET
def oidc_logout(request):
    id_token = request.session.get("oidc_id_token")
    django_logout(request)
    post_logout_uri = settings.OIDC_POST_LOGOUT_REDIRECT_URL or request.build_absolute_uri("/")
    if id_token:
        return oauth.agromega.logout_redirect(
            request,
            post_logout_redirect_uri=post_logout_uri,
            id_token_hint=id_token,
        )
    return redirect(post_logout_uri)
